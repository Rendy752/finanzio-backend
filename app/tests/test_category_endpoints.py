import pytest
from httpx import Client
from app.api.v1.dependencies import TEST_USER_A_ID 
import uuid

temp_category_income_id = None
temp_category_expense_id = None

VALID_CATEGORY_INCOME_DATA = {
    "category_name": "Salary",
    "type": "INCOME"
}

VALID_CATEGORY_EXPENSE_DATA = {
    "category_name": "Groceries",
    "type": "EXPENSE"
}

class TestCategoryCRUD:

    def test_1_create_category_success(self, client: Client):
        global temp_category_income_id 
        
        response = client.post("/api/v1/categories/", json=VALID_CATEGORY_INCOME_DATA) 
        
        assert response.status_code == 201
        data = response.json()
        temp_category_income_id = data["data"]["category_id"]
        
        assert data["data"]["category_name"] == "Salary"
        assert data["data"]["type"] == "INCOME"
        
    def test_2_create_category_expense_for_dependency(self, client: Client):
        """Membuat kategori Expense secara eksplisit untuk test Budget/Transaction."""
        global temp_category_expense_id
        
        response = client.post("/api/v1/categories/", json=VALID_CATEGORY_EXPENSE_DATA) 
        assert response.status_code == 201
        temp_category_expense_id = response.json()["data"]["category_id"]

    def test_3_read_all_categories_with_search_and_pagination(self, client: Client):
        response_a = client.post("/api/v1/categories/", json={"category_name": "ZZZ_Food A Unique", "type": "EXPENSE"})
        category_id_a = response_a.json()["data"]["category_id"] if response_a.status_code == 201 else None

        response_b = client.post("/api/v1/categories/", json={"category_name": "ZZZ_Food B Unique", "type": "EXPENSE"})
        category_id_b = response_b.json()["data"]["category_id"] if response_b.status_code == 201 else None

        # Test Search (q=ZZZ_Food A Unique)
        response_search = client.get("/api/v1/categories/?q=ZZZ_Food A Unique")
        assert response_search.status_code == 200
        
        assert response_search.json()["total_count"] == 1 
        assert len(response_search.json()["data"]) == 1

        response_page = client.get("/api/v1/categories/?limit=1&offset=1")
        assert response_page.status_code == 200
        assert len(response_page.json()["data"]) == 1
        
        if category_id_a:
            client.delete(f"/api/v1/categories/{category_id_a}")
        if category_id_b:
            client.delete(f"/api/v1/categories/{category_id_b}")

    def test_4_read_category_success(self, client: Client):
        global temp_category_income_id
        assert temp_category_income_id is not None
        
        response = client.get(f"/api/v1/categories/{temp_category_income_id}")
        assert response.status_code == 200
        assert response.json()["data"]["type"] == "INCOME"
        
    def test_5_update_category_success(self, client: Client):
        global temp_category_income_id
        assert temp_category_income_id is not None
        
        update_data = {"category_name": "Monthly Salary", "type": "INCOME"}

        response = client.put(f"/api/v1/categories/{temp_category_income_id}", json=update_data)

        assert response.status_code == 200
        assert response.json()["data"]["category_name"] == "Monthly Salary"

    def test_6_delete_category_success(self, client: Client):
        global temp_category_income_id
        assert temp_category_income_id is not None
        
        response = client.delete(f"/api/v1/categories/{temp_category_income_id}")

        assert response.status_code == 204
        
        verify_response = client.get(f"/api/v1/categories/{temp_category_income_id}")
        assert verify_response.status_code == 404