import pytest
from fastapi.testclient import TestClient 
from app.main import app 

# Import dependencies and models
from app.core.db import AsyncSessionLocal, get_db
from app.models.user import User # Import the User model
from app.api.v1.dependencies import get_current_user 
from app.schemas.user import UserResponse
from datetime import datetime
from typing import AsyncGenerator
import uuid
from sqlalchemy.future import select 

# --- PENGATURAN PENGGUNA TES ---
TEST_USER_A_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

def mock_get_current_user():
    """Returns a fixed User A for authentication."""
    return UserResponse(
        user_id=TEST_USER_A_ID, 
        email="test_user_a@test.com",
        first_name="Test",
        last_name="UserA",
        is_active=True,
        # NOTE: Deprecation warning will still appear, this is unavoidable until 
        # Python 3.12 drops support for utcnow().
        created_at=datetime.utcnow() 
    )

# -----------------------------------------------------
# FIX: MENGUBAH DB OVERRIDE UNTUK MENGIZINKAN PERSISTENSI DATA
# -----------------------------------------------------

async def override_get_db() -> AsyncGenerator:
    """Dependency override yang memastikan mock user ada dan menyediakan sesi.
    (Diperbarui untuk mengizinkan commit data antar test berurutan.)
    """
    
    # Buka sesi asynchronous
    async with AsyncSessionLocal() as session:
        # Mulai transaksi eksplisit untuk setup user.
        await session.begin() 

        # 1. Pastikan mock user ada di database untuk memenuhi Foreign Key.
        user_exists = await session.execute(
            select(User).where(User.user_id == TEST_USER_A_ID)
        )
        if not user_exists.scalar_one_or_none():
            mock_user = User(
                user_id=TEST_USER_A_ID,
                email=mock_get_current_user().email,
                password_hash="mock_hash",
                is_active=True
            )
            session.add(mock_user)
            await session.flush()
            # FIX 1: Commit the mock user to make it permanent for FK constraints.
            await session.commit()
        else:
            # Jika user sudah ada, batalkan transaksi setup agar tidak mengubah apa-apa
            await session.rollback()
        
        # FIX 2 & 3: Commit mocking dan rollback akhir dihilangkan. 
        # Ini memungkinkan `db.commit()` di CRUD layer menjadi commit sungguhan 
        # yang membuat wallet dari test_1 persisten untuk test_2, 5, dan 6.
        
        try:
            # 3. Yield the session (sekarang dengan commit nyata) ke endpoint.
            yield session
            
            # Baris `await session.rollback()` yang menyebabkan bug telah dihapus.
            
        except Exception:
            # Jika tes gagal, batalkan transaksi dan sebarkan error.
            await session.rollback()
            raise
        finally:
            # 4. Tutup koneksi sesi.
            await session.close()


@pytest.fixture(scope="session")
def client(): 
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
        
    app.dependency_overrides.clear()