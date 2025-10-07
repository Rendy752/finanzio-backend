import pytest
from httpx import Client
from app.api.v1.dependencies import TEST_USER_A_ID 
import uuid

temp_wallet_id = None 
temp_wallet_id_2 = None 

VALID_WALLET_DATA = {
    "wallet_name": "Bank Utama",
    "currency": "IDR",
    "initial_balance": 5000000.50
}

class TestWalletCRUD:
    
    def test_1_create_wallet_success(self, client: Client):
        global temp_wallet_id 
        
        response = client.post("/api/v1/wallets/", json=VALID_WALLET_DATA) 
        
        assert response.status_code == 201
        data = response.json()
        temp_wallet_id = data["data"]["wallet_id"]
        
        assert data["data"]["wallet_name"] == VALID_WALLET_DATA["wallet_name"]
        assert data["data"]["user_id"] == str(TEST_USER_A_ID)


    def test_2_create_wallet_small_for_dependency(self, client: Client):
        """Membuat wallet kedua secara eksplisit untuk test Transaction."""
        global temp_wallet_id_2
        
        response = client.post("/api/v1/wallets/", json={"wallet_name": "Cash Small", "currency": "USD", "initial_balance": 100.00})
        assert response.status_code == 201
        temp_wallet_id_2 = response.json()["data"]["wallet_id"]


    def test_3_read_wallet_success(self, client: Client):
        global temp_wallet_id 
        assert temp_wallet_id is not None
        
        response = client.get(f"/api/v1/wallets/{temp_wallet_id}")
        
        assert response.status_code == 200
        assert response.json()["data"]["current_balance"] == '5000000.50'


    def test_4_read_all_wallets_with_search_and_pagination(self, client: Client):
        response_1 = client.post("/api/v1/wallets/", json={"wallet_name": "ZZZ_Savings Unique 1", "currency": "IDR", "initial_balance": 500.00})
        wallet_id_1 = response_1.json()["data"]["wallet_id"] if response_1.status_code == 201 else None

        response_2 = client.post("/api/v1/wallets/", json={"wallet_name": "ZZZ_Savings Unique 2", "currency": "IDR", "initial_balance": 500.00})
        wallet_id_2 = response_2.json()["data"]["wallet_id"] if response_2.status_code == 201 else None

        response = client.get("/api/v1/wallets/?q=ZZZ_Savings Unique")
        assert response.status_code == 200
        assert response.json()["total_count"] == 2 
        assert len(response.json()["data"]) == 2

        if wallet_id_1:
            client.delete(f"/api/v1/wallets/{wallet_id_1}")
        if wallet_id_2:
            client.delete(f"/api/v1/wallets/{wallet_id_2}")


    def test_5_update_wallet_success(self, client: Client):
        global temp_wallet_id
        assert temp_wallet_id is not None
        
        update_data = {
            "wallet_name": "Bank Utama Re-named",
            "currency": "EUR" 
        }

        response = client.put(f"/api/v1/wallets/{temp_wallet_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        
        assert data["data"]["wallet_name"] == "Bank Utama Re-named"
        assert data["data"]["current_balance"] == '5000000.50' 


    def test_6_delete_wallet_success(self, client: Client):
        global temp_wallet_id
        assert temp_wallet_id is not None
        
        response = client.delete(f"/api/v1/wallets/{temp_wallet_id}")

        assert response.status_code == 204
        
        # Verify deletion 
        verify_response = client.get(f"/api/v1/wallets/{temp_wallet_id}")
        assert verify_response.status_code == 404
        
        temp_wallet_id = None 
    
    def test_7_read_wallet_not_found(self, client: Client):
        non_existent_id = uuid.uuid4()
        response = client.get(f"/api/v1/wallets/{non_existent_id}")

        assert response.status_code == 404