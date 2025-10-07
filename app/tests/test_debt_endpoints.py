import pytest
from httpx import Client
from app.api.v1.dependencies import TEST_USER_A_ID 
import uuid
from decimal import Decimal

temp_debt_id = None

VALID_DEBT_DATA = {
    "contact_name": "Client A",
    "total_amount": 1000.00,
    "is_debt_to_user": True, # Piutang (Receivable)
    "phone_number": "081234567890",
    "due_date": "2025-12-31"
}

class TestDebtCRUD:

    def test_1_create_debt_success(self, client: Client):
        global temp_debt_id 
        
        response = client.post("/api/v1/debts/", json=VALID_DEBT_DATA) 
        
        assert response.status_code == 201
        data = response.json()
        temp_debt_id = data["data"]["ledger_id"]
        
        assert data["data"]["contact_name"] == "Client A"

    def test_2_read_debt_success(self, client: Client):
        global temp_debt_id
        assert temp_debt_id is not None
        
        response = client.get(f"/api/v1/debts/{temp_debt_id}")
        
        assert response.status_code == 200
        assert response.json()["data"]["total_amount"] == '1000.00'

    def test_3_read_all_debts_with_search(self, client: Client):
        client.post("/api/v1/debts/", json={"contact_name": "ZZZ_Client X Unique", "total_amount": 100.00, "is_debt_to_user": True})
        client.post("/api/v1/debts/", json={"contact_name": "ZZZ_Vendor Y Unique", "total_amount": 500.00, "is_debt_to_user": False})

        # Test Search (q=Vendor Y Unique)
        response = client.get("/api/v1/debts/?q=ZZZ_Vendor Y Unique")
        assert response.status_code == 200

        assert len(response.json()["data"]) == 1
        assert response.json()["data"][0]["contact_name"] == "ZZZ_Vendor Y Unique"

        for debt in response.json()["data"]:
            client.delete(f"/api/v1/debts/{debt['ledger_id']}")

    def test_4_update_debt_record_payment(self, client: Client):
        global temp_debt_id
        assert temp_debt_id is not None
        
        # Bayar sebagian: 500.00
        update_data = {"amount_paid": 500.00}

        response = client.put(f"/api/v1/debts/{temp_debt_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        
        assert data["data"]["amount_paid"] == '500.00'
        assert data["data"]["is_settled"] is False 

    def test_5_update_debt_mark_settled(self, client: Client):
        global temp_debt_id
        assert temp_debt_id is not None
        
        # Tandai sebagai lunas
        update_data = {"is_settled": True}

        response = client.put(f"/api/v1/debts/{temp_debt_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        
        # amount_paid harus menjadi total_amount (1000.00)
        assert data["data"]["amount_paid"] == '1000.00' 
        assert data["data"]["is_settled"] is True

    def test_6_delete_debt_success(self, client: Client):
        global temp_debt_id
        assert temp_debt_id is not None
        
        response = client.delete(f"/api/v1/debts/{temp_debt_id}")
        assert response.status_code == 204
        temp_debt_id = None