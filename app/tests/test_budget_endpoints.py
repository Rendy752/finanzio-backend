import pytest
from httpx import Client
from app.api.v1.dependencies import TEST_USER_A_ID 
import uuid
from decimal import Decimal

# Pastikan ID ini akan diisi oleh test_api_category.py
temp_category_expense_id = None 
temp_budget_id = None

VALID_BUDGET_DATA = {
    "amount_limit": 500.00,
    "start_date": "2025-10-01",
    "end_date": "2025-10-31"
}

@pytest.fixture(scope="class")
def setup_budget_dependencies(client: Client):
    """Membuat Category dependency untuk memastikan ID tersedia."""
    global temp_category_expense_id

    response = client.post("/api/v1/categories/", json={"category_name": "Test Budget Cat", "type": "EXPENSE"})
    assert response.status_code == 201, f"Setup failed: Category POST failed. {response.json()}"
    temp_category_expense_id = response.json()["data"]["category_id"]

    yield client


class TestBudgetCRUD:
    def test_1_create_budget_success(self, setup_budget_dependencies: Client):
        client = setup_budget_dependencies 
        global temp_budget_id
        global temp_budget_id
        global temp_category_expense_id
        assert temp_category_expense_id is not None

        budget_data = VALID_BUDGET_DATA.copy()
        budget_data["category_id"] = temp_category_expense_id

        response = client.post("/api/v1/budgets/", json=budget_data) 
        
        assert response.status_code == 201
        data = response.json()
        temp_budget_id = data["data"]["budget_id"]
        
        assert data["data"]["amount_limit"] == '500.00'
        assert data["data"]["category_id"] == str(temp_category_expense_id)

    def test_2_read_budget_success(self, setup_budget_dependencies: Client):
        client = setup_budget_dependencies 
        global temp_budget_id
        global temp_budget_id
        assert temp_budget_id is not None
        
        response = client.get(f"/api/v1/budgets/{temp_budget_id}")
        
        assert response.status_code == 200
        assert response.json()["data"]["start_date"] == "2025-10-01"

    def test_3_read_all_budgets_with_pagination(self, setup_budget_dependencies: Client):
        client = setup_budget_dependencies 
        global temp_budget_id
        budget_data = VALID_BUDGET_DATA.copy()
        budget_data["category_id"] = temp_category_expense_id
        budget_data["amount_limit"] = 1000.00
        client.post("/api/v1/budgets/", json=budget_data) 
        
        response = client.get("/api/v1/budgets/?limit=1&offset=1")
        assert response.status_code == 200
        assert response.json()["total_count"] == 2
        assert len(response.json()["data"]) == 1 

    def test_4_update_budget_success(self, setup_budget_dependencies: Client):
        client = setup_budget_dependencies 
        global temp_budget_id
        global temp_budget_id
        assert temp_budget_id is not None
        
        update_data = {
            "category_id": str(temp_category_expense_id),
            "amount_limit": 750.00,
            "start_date": "2025-10-01",
            "end_date": "2025-11-30" 
        }

        response = client.put(f"/api/v1/budgets/{temp_budget_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        
        assert data["data"]["amount_limit"] == '750.00'
        assert data["data"]["end_date"] == "2025-11-30" 

    def test_5_delete_budget_success(self, setup_budget_dependencies: Client):
        client = setup_budget_dependencies 
        global temp_budget_id
        global temp_budget_id
        assert temp_budget_id is not None
        
        response = client.delete(f"/api/v1/budgets/{temp_budget_id}")
        assert response.status_code == 204
        temp_budget_id = None