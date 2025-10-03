from httpx import Client
from app.api.v1.dependencies import TEST_USER_A_ID 
import uuid

temp_wallet_id = None 
TEST_USER_B_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")

VALID_WALLET_DATA = {
    "wallet_name": "Bank Mandiri Test",
    "currency": "IDR",
    "initial_balance": 5000000.50
}

class TestWalletCRUD:
    # -------------------------------------------------------------------------
    # Test 1: POST (Create) - Gunakan cls untuk menyimpan ID
    # -------------------------------------------------------------------------
    def test_1_create_wallet_success(self, client: Client):
        """Test successful creation of a new wallet."""
        # Akses variabel global
        global temp_wallet_id 
        
        response = client.post("/api/v1/wallets/", json=VALID_WALLET_DATA) 
        
        # Jika tes ini gagal, beri informasi lebih lanjut. (Ini membantu debugging)
        if response.status_code != 201:
            print(f"Test 1 Failed with status {response.status_code}. Response: {response.json()}")
            assert response.status_code == 201, "Failed to create wallet."

        data = response.json()
        
        assert data["success"] is True
        assert data["message"] == "Wallet created successfully."
        
        # Simpan ID ke variabel GLOBAL
        temp_wallet_id = data["data"]["wallet_id"]
        
        # Assertion lainnya
        assert data["data"]["wallet_name"] == VALID_WALLET_DATA["wallet_name"]
        assert data["data"]["user_id"] == str(TEST_USER_A_ID)


    # -------------------------------------------------------------------------
    # Test 2: GET (Read Single) - Gunakan cls untuk mengambil ID
    # -------------------------------------------------------------------------
    def test_2_read_wallet_success(self, client: Client):
        # Akses variabel global
        global temp_wallet_id 
        
        """Test retrieval of the created wallet by its ID."""
        # Perbaiki kegagalan assert None is not None
        assert temp_wallet_id is not None, "temp_wallet_id must be set by Test 1"
        
        response = client.get(f"/api/v1/wallets/{temp_wallet_id}")
        
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["data"]["wallet_id"] == temp_wallet_id
        assert data["data"]["current_balance"] == '5000000.50'


    # -------------------------------------------------------------------------
    # Test 3: GET (Read Not Found) - Tidak bergantung pada state
    # -------------------------------------------------------------------------
    def test_3_read_wallet_not_found(self, client: Client):
        """Test retrieval of a non-existent wallet ID."""
        # ... (Kode tetap sama) ...
        non_existent_id = uuid.uuid4()
        response = client.get(f"/api/v1/wallets/{non_existent_id}")

        assert response.status_code == 404
        assert "Wallet not found or not accessible." in response.json()["detail"]


    # -------------------------------------------------------------------------
    # Test 4: GET (Read All) - Gunakan cls
    # -------------------------------------------------------------------------
    def test_4_read_all_wallets_success(self, client: Client):
        # Akses variabel global (hanya diperlukan jika ingin memeriksa temp_wallet_id,
        # tetapi untuk POST kedua tidak perlu, jadi kita biarkan saja)
        
        """Test retrieval of all wallets for the authenticated user."""
        # Create a second wallet for User A 
        client.post("/api/v1/wallets/", json={"wallet_name": "Cash", "currency": "USD", "initial_balance": 100.00})

        response = client.get("/api/v1/wallets/")

        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["total_count"] >= 2 
        
        # Check ownership
        for wallet in data["data"]:
            assert wallet["user_id"] == str(TEST_USER_A_ID)


    # -------------------------------------------------------------------------
    # Test 5: PUT (Update) - MENGGUNAKAN STATE GLOBAL
    # -------------------------------------------------------------------------
    def test_5_update_wallet_success(self, client: Client):
        global temp_wallet_id
        assert temp_wallet_id is not None
        
        update_data = {
            "wallet_name": "Bank Mandiri Pro",
            "currency": "USD" 
        }

        response = client.put(f"/api/v1/wallets/{temp_wallet_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        
        assert data["data"]["wallet_name"] == "Bank Mandiri Pro"
        assert data["data"]["currency"] == "USD"
        assert data["data"]["current_balance"] == '5000000.50' 


    # -------------------------------------------------------------------------
    # Test 6: DELETE - MENGGUNAKAN STATE GLOBAL
    # -------------------------------------------------------------------------
    def test_6_delete_wallet_success(self, client: Client):
        global temp_wallet_id
        assert temp_wallet_id is not None
        
        response = client.delete(f"/api/v1/wallets/{temp_wallet_id}")

        # Standard response for successful deletion (No Content)
        assert response.status_code == 204
        assert response.content == b''

        # Verify deletion by attempting to retrieve it
        verify_response = client.get(f"/api/v1/wallets/{temp_wallet_id}")
        assert verify_response.status_code == 404
        assert "Wallet not found or not accessible." in verify_response.json()["detail"]
        
        # Set ID kembali ke None setelah dihapus (meskipun rollback akan membersihkannya)
        temp_wallet_id = None 


    # -------------------------------------------------------------------------
    # Test 7: DELETE (Not Found)
    # -------------------------------------------------------------------------
    def test_7_delete_non_existent_wallet(self, client: Client):
        """Test deleting a wallet that doesn't exist."""
        # ... (Kode tetap sama) ...
        non_existent_id = uuid.uuid4()
        response = client.delete(f"/api/v1/wallets/{non_existent_id}")

        assert response.status_code == 404
        assert "Wallet not found or not accessible for deletion." in response.json()["detail"]