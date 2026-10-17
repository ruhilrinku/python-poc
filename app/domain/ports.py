from abc import ABC, abstractmethod

from app.domain.entities import Department, Employee


class EmployeeRepository(ABC):
    """Driven port for employee persistence."""

    @abstractmethod
    def add(self, employee: Employee) -> Employee: ...

    @abstractmethod
    def get_by_id(self, employee_id: int) -> Employee | None: ...

    @abstractmethod
    def get_by_code(self, employee_code: str) -> Employee | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Employee | None: ...

    @abstractmethod
    def update(self, employee: Employee) -> Employee: ...

    @abstractmethod
    def set_departments(
        self, employee_id: int, departments: list[Department]
    ) -> Employee: ...

    @abstractmethod
    def delete(self, employee_id: int) -> None: ...


class DepartmentRepository(ABC):
    """Driven port for department persistence."""

    @abstractmethod
    def get_by_id(self, department_id: int) -> Department | None: ...

    @abstractmethod
    def get_by_ids(self, department_ids: list[int]) -> list[Department]: ...

    @abstractmethod
    def list_employees(self, department_id: int) -> list[Employee]: ...
