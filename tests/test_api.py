from fastapi.testclient import TestClient


def _create_employee(client: TestClient, **overrides) -> dict:
    payload = {
        "employee_code": "EMP001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "9999999999",
        "department_ids": [1, 2],
    }
    payload.update(overrides)
    response = client.post("/api/v1/employees", json=payload)
    return response


def test_create_employee(client: TestClient):
    response = _create_employee(client)
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["employee_code"] == "EMP001"
    assert {d["id"] for d in body["departments"]} == {1, 2}


def test_create_employee_duplicate_email_returns_conflict(client: TestClient):
    _create_employee(client)
    response = _create_employee(client, employee_code="EMP002")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DUPLICATE_EMAIL"


def test_create_employee_unknown_department(client: TestClient):
    response = _create_employee(client, department_ids=[999])
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DEPARTMENT_NOT_FOUND"


def test_create_employee_invalid_payload(client: TestClient):
    response = client.post("/api/v1/employees", json={"first_name": "John"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_get_employee(client: TestClient):
    _create_employee(client)
    response = client.get("/api/v1/employees/1")
    assert response.status_code == 200
    assert response.json()["email"] == "john.doe@example.com"


def test_get_employee_not_found(client: TestClient):
    response = client.get("/api/v1/employees/999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "EMPLOYEE_NOT_FOUND"


def test_update_employee(client: TestClient):
    _create_employee(client)
    response = client.put(
        "/api/v1/employees/1",
        json={"first_name": "Johnny", "email": "johnny.doe@example.com"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Employee updated successfully"}
    assert client.get("/api/v1/employees/1").json()["first_name"] == "Johnny"


def test_update_employee_departments(client: TestClient):
    _create_employee(client)
    response = client.put(
        "/api/v1/employees/1/departments", json={"department_ids": [2, 3]}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Departments updated successfully"
    assert body["employee_id"] == 1
    assert sorted(body["department_ids"]) == [2, 3]


def test_get_department_employees(client: TestClient):
    _create_employee(client)
    _create_employee(
        client,
        employee_code="EMP002",
        email="jane.smith@example.com",
        department_ids=[1],
    )
    response = client.get("/api/v1/departments/1/employees")
    assert response.status_code == 200
    body = response.json()
    assert body["department_id"] == 1
    assert body["department_name"] == "Engineering"
    assert {e["employee_code"] for e in body["employees"]} == {"EMP001", "EMP002"}


def test_get_department_employees_not_found(client: TestClient):
    response = client.get("/api/v1/departments/999/employees")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DEPARTMENT_NOT_FOUND"


def test_delete_employee(client: TestClient):
    _create_employee(client)
    response = client.delete("/api/v1/employees/1")
    assert response.status_code == 204
    assert client.get("/api/v1/employees/1").status_code == 404


def test_delete_employee_not_found(client: TestClient):
    response = client.delete("/api/v1/employees/999")
    assert response.status_code == 404
