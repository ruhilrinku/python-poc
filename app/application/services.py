import logging

from app.domain.entities import Department, Employee
from app.domain.exceptions import (
    DepartmentNotFound,
    DuplicateEmail,
    DuplicateEmployeeCode,
    EmployeeNotFound,
)
from app.domain.ports import DepartmentRepository, EmployeeRepository

logger = logging.getLogger(__name__)


class EmployeeService:
    """Application service orchestrating employee use cases via driven ports."""

    def __init__(
        self, employees: EmployeeRepository, departments: DepartmentRepository
    ):
        self._employees = employees
        self._departments = departments

    def create_employee(
        self,
        *,
        employee_code: str,
        first_name: str,
        last_name: str,
        email: str,
        phone: str | None = None,
        department_ids: list[int] | None = None,
    ) -> Employee:
        if self._employees.get_by_code(employee_code):
            raise DuplicateEmployeeCode(
                f"Employee code '{employee_code}' already exists"
            )
        if self._employees.get_by_email(email):
            raise DuplicateEmail(f"Email '{email}' already exists")

        departments = self._resolve_departments(department_ids or [])
        employee = Employee(
            id=None,
            employee_code=employee_code,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            departments=departments,
        )
        created = self._employees.add(employee)
        logger.info(
            "employee.created", extra={"extra_fields": {"employee_id": created.id}}
        )
        return created

    def update_employee(
        self,
        employee_id: int,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
    ) -> Employee:
        employee = self._get_or_raise(employee_id)

        if email is not None and email != employee.email:
            existing = self._employees.get_by_email(email)
            if existing and existing.id != employee_id:
                raise DuplicateEmail(f"Email '{email}' already exists")
            employee.email = email
        if first_name is not None:
            employee.first_name = first_name
        if last_name is not None:
            employee.last_name = last_name
        if phone is not None:
            employee.phone = phone

        updated = self._employees.update(employee)
        logger.info(
            "employee.updated", extra={"extra_fields": {"employee_id": employee_id}}
        )
        return updated

    def update_departments(
        self, employee_id: int, department_ids: list[int]
    ) -> Employee:
        self._get_or_raise(employee_id)
        departments = self._resolve_departments(department_ids)
        updated = self._employees.set_departments(employee_id, departments)
        logger.info(
            "employee.departments_updated",
            extra={
                "extra_fields": {
                    "employee_id": employee_id,
                    "department_ids": department_ids,
                }
            },
        )
        return updated

    def get_employee(self, employee_id: int) -> Employee:
        return self._get_or_raise(employee_id)

    def get_employees_by_department(
        self, department_id: int
    ) -> tuple[Department, list[Employee]]:
        department = self._departments.get_by_id(department_id)
        if department is None:
            raise DepartmentNotFound(f"Department '{department_id}' not found")
        employees = self._departments.list_employees(department_id)
        return department, employees

    def delete_employee(self, employee_id: int) -> None:
        self._get_or_raise(employee_id)
        self._employees.delete(employee_id)
        logger.info(
            "employee.deleted", extra={"extra_fields": {"employee_id": employee_id}}
        )

    def _get_or_raise(self, employee_id: int) -> Employee:
        employee = self._employees.get_by_id(employee_id)
        if employee is None:
            raise EmployeeNotFound(f"Employee '{employee_id}' not found")
        return employee

    def _resolve_departments(self, department_ids: list[int]) -> list[Department]:
        if not department_ids:
            return []
        unique_ids = list(dict.fromkeys(department_ids))
        found = self._departments.get_by_ids(unique_ids)
        found_ids = {d.id for d in found}
        missing = [i for i in unique_ids if i not in found_ids]
        if missing:
            raise DepartmentNotFound(f"Departments do not exist: {missing}")
        return found
