import pytest
from httpx import Client
from app.api.v1.dependencies import TEST_USER_A_ID 
import uuid
from decimal import Decimal

temp_wallet_id_2 = None 
temp_category_expense_id = None 
temp_transaction_id = None

VALID_TRANSACTION_DATA = {
    "transaction_type": "EXPENSE",
    "amount": 50.00,
    "description": "Weekly coffee expense.",
    "transaction_date": "2025-10-07T10:00:00Z"
}

@pytest.fixture(scope="class")
def setup_transaction_dependencies(client: Client):
    """Membuat Wallet dan Category dependency yang dibutuhkan sebelum menjalankan test class."""
    global temp_wallet_id_2
    global temp_wallet_id_2
    global temp_category_expense_id
    global temp_transaction_id

    response = client.post("/api/v1/wallets/", json={"wallet_name": "Cash for Txn", "currency": "USD", "initial_balance": 100.00})
    assert response.status_code == 201, f"Setup failed: Wallet POST failed. {response.json()}"
    temp_wallet_id_2 = response.json()["data"]["wallet_id"]
    
    response_2 = client.post("/api/v1/categories/", json={"category_name": "Test Txn Cat", "type": "EXPENSE"}) 
    assert response_2.status_code == 201, f"Setup failed: Category POST failed. {response_2.json()}"
    temp_category_expense_id = response_2.json()["data"]["category_id"]

    yield client

    response_search = client.get("/api/v1/transactions/?q=ZZZ_Freelance payment unique")
    if response_search.status_code == 200:
        for transaction in response_search.json()["data"]:
             client.delete(f"/api/v1/transactions/{transaction['transaction_id']}")

    if temp_transaction_id:
        client.delete(f"/api/v1/transactions/{temp_transaction_id}")
        temp_transaction_id = None
        
    if temp_wallet_id_2:
        client.delete(f"/api/v1/wallets/{temp_wallet_id_2}")
        temp_wallet_id_2 = None # Added for completeness
        
    if temp_category_expense_id:
        client.delete(f"/api/v1/categories/{temp_category_expense_id}")
        temp_category_expense_id = None
        temp_category_expense_id = None

class TestTransactionCRUD:

    def test_1_create_transaction_updates_wallet_success(self, setup_transaction_dependencies: Client):
        client = setup_transaction_dependencies
        global temp_transaction_id
        global temp_wallet_id_2 
        global temp_category_expense_id
        
        assert temp_wallet_id_2 is not None
        assert temp_category_expense_id is not None
        
        transaction_data = VALID_TRANSACTION_DATA.copy()
        transaction_data["wallet_id"] = str(temp_wallet_id_2)
        transaction_data["category_id"] = str(temp_category_expense_id)
        
        # 1. Post Transaction: Expense 50.00
        response = client.post("/api/v1/transactions/", json=transaction_data) 
        
        assert response.status_code == 201
        data = response.json()
        temp_transaction_id = data["data"]["transaction_id"]
        
        # 2. VERIFIKASI SALDO WALLET (Wallet: 100.00 - 50.00 = 50.00)
        wallet_response = client.get(f"/api/v1/wallets/{temp_wallet_id_2}")
        assert wallet_response.json()["data"]["current_balance"] == '50.00' 

    def test_2_read_transaction_success(self, setup_transaction_dependencies: Client):
        client = setup_transaction_dependencies
        global temp_transaction_id
        assert temp_transaction_id is not None
        
        response = client.get(f"/api/v1/transactions/{temp_transaction_id}")
        assert response.status_code == 200
        
    def test_3_read_all_transactions_with_search(self, setup_transaction_dependencies: Client):
        client = setup_transaction_dependencies
        
        # Buat transaksi kedua (INCOME) untuk menguji query
        income_transaction = {
            "wallet_id": str(temp_wallet_id_2),
            "category_id": str(temp_category_expense_id), 
            "transaction_type": "INCOME",
            "amount": 100.00,
            "description": "ZZZ_Freelance payment unique." # Tambahkan ZZZ_Unique untuk cleanup
        }
        
        response_new = client.post("/api/v1/transactions/", json=income_transaction) 
        # Simpan ID transaksi baru untuk cleanup
        new_transaction_id = response_new.json()["data"]["transaction_id"] if response_new.status_code == 201 else None

        # Test Search (q=payment)
        response = client.get("/api/v1/transactions/?q=ZZZ_Freelance payment unique")
        assert response.status_code == 200
        assert response.json()["total_count"] == 1 # Total 1 yang difilter
        
        # Current Wallet Balance should be: 50.00 (dari test 1) + 100.00 = 150.00
        wallet_response = client.get(f"/api/v1/wallets/{temp_wallet_id_2}")
        assert wallet_response.json()["data"]["current_balance"] == '150.00' 

        # =========================================================================
        # FIX 2: Tambahkan Cleanup untuk data unik di test ini
        # =========================================================================
        # Hapus transaksi yang baru dibuat di sini (EXPENSE 100.00)
        if new_transaction_id:
            client.delete(f"/api/v1/transactions/{new_transaction_id}")
            
        # Verifikasi Saldo setelah cleanup: 150.00 - 100.00 (revert income) = 50.00
        wallet_response_cleanup = client.get(f"/api/v1/wallets/{temp_wallet_id_2}")
        assert wallet_response_cleanup.json()["data"]["current_balance"] == '50.00'

    def test_4_update_transaction_recalculates_balance(self, setup_transaction_dependencies: Client):
        client = setup_transaction_dependencies
        global temp_transaction_id
        assert temp_transaction_id is not None
        
        # Ubah transaksi pertama (50.00 Expense) menjadi 25.00
        update_data = VALID_TRANSACTION_DATA.copy()
        update_data["wallet_id"] = str(temp_wallet_id_2)
        update_data["category_id"] = str(temp_category_expense_id)
        update_data["amount"] = 25.00 # NEW AMOUNT
        
        response = client.put(f"/api/v1/transactions/{temp_transaction_id}", json=update_data)

        # Verifikasi Saldo: (Saldo sebelumnya 50.00)
        # Revert Old: +50.00 (revert expense) = 100.00
        # Apply New: -25.00 (new expense) = 75.00
        wallet_response = client.get(f"/api/v1/wallets/{temp_wallet_id_2}")
        assert wallet_response.json()["data"]["current_balance"] == '75.00' 

    def test_5_delete_transaction_reverts_balance(self, setup_transaction_dependencies: Client):
        client = setup_transaction_dependencies
        global temp_transaction_id
        assert temp_transaction_id is not None
        
        # Saldo saat ini 75.00. Transaksi yang dihapus adalah EXPENSE 25.00.
        response = client.delete(f"/api/v1/transactions/{temp_transaction_id}")
        assert response.status_code == 204
        
        # Verifikasi Saldo: (75.00 + 25.00 (revert expense)) = 100.00 (Kembali ke initial_balance)
        wallet_response = client.get(f"/api/v1/wallets/{temp_wallet_id_2}")
        assert wallet_response.json()["data"]["current_balance"] == '100.00' 
        
        temp_transaction_id = None