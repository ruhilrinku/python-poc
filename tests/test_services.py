import pytest

from app.application.services import EmployeeService
from app.domain.entities import Department, Employee
from app.domain.exceptions import (
    DepartmentNotFound,
    DuplicateEmail,
    DuplicateEmployeeCode,
    EmployeeNotFound,
)
from app.domain.ports import DepartmentRepository, EmployeeRepository


class FakeEmployeeRepository(EmployeeRepository):
    def __init__(self) -> None:
        self._store: dict[int, Employee] = {}
        self._seq = 0

    def add(self, employee: Employee) -> Employee:
        self._seq += 1
        employee.id = self._seq
        self._store[employee.id] = employee
        return employee

    def get_by_id(self, employee_id: int) -> Employee | None:
        return self._store.get(employee_id)

    def get_by_code(self, employee_code: str) -> Employee | None:
        return next(
            (e for e in self._store.values() if e.employee_code == employee_code),
            None,
        )

    def get_by_email(self, email: str) -> Employee | None:
        return next(
            (e for e in self._store.values() if e.email == email), None
        )

    def update(self, employee: Employee) -> Employee:
        self._store[employee.id] = employee
        return employee

    def set_departments(
        self, employee_id: int, departments: list[Department]
    ) -> Employee:
        employee = self._store[employee_id]
        employee.departments = departments
        return employee

    def delete(self, employee_id: int) -> None:
        self._store.pop(employee_id, None)


class FakeDepartmentRepository(DepartmentRepository):
    def __init__(self, departments: list[Department]) -> None:
        self._store = {d.id: d for d in departments}
        self._members: dict[int, list[Employee]] = {}

    def get_by_id(self, department_id: int) -> Department | None:
        return self._store.get(department_id)

    def get_by_ids(self, department_ids: list[int]) -> list[Department]:
        return [self._store[i] for i in department_ids if i in self._store]

    def list_employees(self, department_id: int) -> list[Employee]:
        return self._members.get(department_id, [])


@pytest.fixture
def departments() -> list[Department]:
    return [
        Department(id=1, department_code="ENG", name="Engineering"),
        Department(id=2, department_code="OPS", name="Operations"),
        Department(id=3, department_code="HR", name="Human Resources"),
    ]


@pytest.fixture
def service(departments: list[Department]) -> EmployeeService:
    return EmployeeService(
        employees=FakeEmployeeRepository(),
        departments=FakeDepartmentRepository(departments),
    )


def test_create_employee_assigns_departments(service: EmployeeService):
    employee = service.create_employee(
        employee_code="EMP001",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        department_ids=[1, 2],
    )
    assert employee.id == 1
    assert {d.id for d in employee.departments} == {1, 2}


def test_create_employee_duplicate_code(service: EmployeeService):
    service.create_employee(
        employee_code="EMP001",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
    )
    with pytest.raises(DuplicateEmployeeCode):
        service.create_employee(
            employee_code="EMP001",
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
        )


def test_create_employee_duplicate_email(service: EmployeeService):
    service.create_employee(
        employee_code="EMP001",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
    )
    with pytest.raises(DuplicateEmail):
        service.create_employee(
            employee_code="EMP002",
            first_name="Jane",
            last_name="Doe",
            email="john@example.com",
        )


def test_create_employee_unknown_department(service: EmployeeService):
    with pytest.raises(DepartmentNotFound):
        service.create_employee(
            employee_code="EMP001",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            department_ids=[99],
        )


def test_update_employee_changes_fields(service: EmployeeService):
    created = service.create_employee(
        employee_code="EMP001",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
    )
    updated = service.update_employee(created.id, first_name="Johnny")
    assert updated.first_name == "Johnny"


def test_update_employee_not_found(service: EmployeeService):
    with pytest.raises(EmployeeNotFound):
        service.update_employee(999, first_name="Nobody")


def test_update_departments_replaces_assignments(service: EmployeeService):
    created = service.create_employee(
        employee_code="EMP001",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        department_ids=[1],
    )
    updated = service.update_departments(created.id, [2, 3])
    assert {d.id for d in updated.departments} == {2, 3}


def test_delete_employee(service: EmployeeService):
    created = service.create_employee(
        employee_code="EMP001",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
    )
    service.delete_employee(created.id)
    with pytest.raises(EmployeeNotFound):
        service.get_employee(created.id)
