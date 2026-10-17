from app.domain.entities import Department, Employee


def test_employee_defaults_to_empty_departments():
    employee = Employee(
        id=None,
        employee_code="EMP001",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
    )
    assert employee.departments == []
    assert employee.phone is None


def test_department_optional_fields():
    department = Department(id=1, department_code="ENG", name="Engineering")
    assert department.description is None
    assert department.name == "Engineering"
