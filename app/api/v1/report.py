from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import uuid
import json
import redis.asyncio as redis
from decimal import Decimal

from app.core.db import get_db
from app.core.redis import get_redis_client
from app.crud import report as crud_report
from app.schemas.transfer import TransferCreate
from app.schemas.report import FinancialSummaryResponse
from app.schemas.transaction import TransactionResponse
from app.schemas.common import APIResponse, APIListResponse
from app.api.v1.dependencies import CurrentUser 

router = APIRouter(prefix="/finance", tags=["Finance & Reports"])

DB_SESSION = Depends(get_db)
REDIS_CLIENT = Depends(get_redis_client)

# --- Endpoint Transfer ---

@router.post(
    "/transfer",
    response_model=APIResponse[List[TransactionResponse]],
    status_code=status.HTTP_201_CREATED,
    summary="Perform an atomic money transfer between two wallets."
)
async def create_transfer(
    transfer_in: TransferCreate,
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """
    Menciptakan dua transaksi (Expense dan Income) untuk memindahkan dana antar wallet 
    dalam satu operasi atomik.
    """
    
    transactions = await crud_report.perform_atomic_transfer(
        db,
        user_id=current_user.user_id,
        source_wallet_id=transfer_in.source_wallet_id,
        target_wallet_id=transfer_in.target_wallet_id,
        amount=transfer_in.amount,
        description=transfer_in.description
    )

    if not transactions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transfer failed. Check if both wallets exist and belong to the user, or if source != target."
        )

    # Invalidasi cache dashboard/summary setelah perubahan besar
    r: redis.Redis = await anext(get_redis_client())
    await r.delete(f"summary:{current_user.user_id}")

    return APIResponse(
        message="Transfer successful. Two transactions created.",
        data=[TransactionResponse.model_validate(t) for t in transactions]
    )


# --- Endpoint Report (with Caching) ---

@router.get(
    "/summary",
    response_model=APIResponse[FinancialSummaryResponse],
    summary="Get high-level financial summary with Redis caching."
)
async def get_summary(
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION,
    r: redis.Redis = REDIS_CLIENT
):
    """
    Mengambil ringkasan keuangan dari cache Redis. 
    Jika tidak ada, dihitung dari DB dan disimpan ke cache selama 300 detik.
    """
    user_id_str = str(current_user.user_id)
    cache_key = f"summary:{user_id_str}"
    
    # 1. Coba ambil dari Cache
    cached_data = await r.get(cache_key)
    if cached_data:
        try:
            summary_dict = json.loads(cached_data)
            # Konversi kembali Decimal dari string (karena JSON tidak mendukung Decimal)
            for key in ['total_income', 'total_expense', 'net_balance']:
                 summary_dict[key] = Decimal(summary_dict[key])

            return APIResponse(
                message="Financial summary retrieved from cache.",
                data=FinancialSummaryResponse(**summary_dict)
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            # Jika cache rusak, kita akan menghitung ulang
            print("Cache corrupted, recalculating summary.")

    # 2. Hitung dari Database
    summary_db = await crud_report.get_financial_summary(db, current_user.user_id)

    # 3. Simpan ke Cache (Convert Decimal ke string untuk JSON serialization)
    summary_to_cache = {
        key: str(value) if isinstance(value, Decimal) else value.isoformat() if isinstance(value, datetime) else value
        for key, value in summary_db.items()
    }
    
    await r.set(cache_key, json.dumps(summary_to_cache), ex=300) # Cache selama 5 menit

    return APIResponse(
        message="Financial summary calculated from database.",
        data=FinancialSummaryResponse(**summary_db)
    )
