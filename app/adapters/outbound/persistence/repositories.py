from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.adapters.outbound.persistence.orm_models import (
    DepartmentModel,
    EmployeeModel,
)
from app.domain.entities import Department, Employee
from app.domain.ports import DepartmentRepository, EmployeeRepository


def _to_department(model: DepartmentModel) -> Department:
    return Department(
        id=model.id,
        department_code=model.department_code,
        name=model.name,
        description=model.description,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_employee(model: EmployeeModel, *, with_departments: bool = True) -> Employee:
    departments = (
        [_to_department(d) for d in model.departments] if with_departments else []
    )
    return Employee(
        id=model.id,
        employee_code=model.employee_code,
        first_name=model.first_name,
        last_name=model.last_name,
        email=model.email,
        phone=model.phone,
        departments=departments,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyEmployeeRepository(EmployeeRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, employee: Employee) -> Employee:
        model = EmployeeModel(
            employee_code=employee.employee_code,
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.email,
            phone=employee.phone,
        )
        model.departments = self._load_department_models(
            [d.id for d in employee.departments if d.id is not None]
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return _to_employee(model)

    def get_by_id(self, employee_id: int) -> Employee | None:
        model = self._session.scalars(
            select(EmployeeModel)
            .options(selectinload(EmployeeModel.departments))
            .where(EmployeeModel.id == employee_id)
        ).first()
        return _to_employee(model) if model else None

    def get_by_code(self, employee_code: str) -> Employee | None:
        model = self._session.scalars(
            select(EmployeeModel)
            .options(selectinload(EmployeeModel.departments))
            .where(EmployeeModel.employee_code == employee_code)
        ).first()
        return _to_employee(model) if model else None

    def get_by_email(self, email: str) -> Employee | None:
        model = self._session.scalars(
            select(EmployeeModel)
            .options(selectinload(EmployeeModel.departments))
            .where(EmployeeModel.email == email)
        ).first()
        return _to_employee(model) if model else None

    def update(self, employee: Employee) -> Employee:
        model = self._session.get(EmployeeModel, employee.id)
        if model is None:
            raise ValueError(f"Employee '{employee.id}' not found")
        model.first_name = employee.first_name
        model.last_name = employee.last_name
        model.email = employee.email
        model.phone = employee.phone
        self._session.commit()
        self._session.refresh(model)
        return _to_employee(model)

    def set_departments(
        self, employee_id: int, departments: list[Department]
    ) -> Employee:
        model = self._session.scalars(
            select(EmployeeModel)
            .options(selectinload(EmployeeModel.departments))
            .where(EmployeeModel.id == employee_id)
        ).first()
        if model is None:
            raise ValueError(f"Employee '{employee_id}' not found")
        model.departments = self._load_department_models(
            [d.id for d in departments if d.id is not None]
        )
        self._session.commit()
        self._session.refresh(model)
        return _to_employee(model)

    def delete(self, employee_id: int) -> None:
        model = self._session.get(EmployeeModel, employee_id)
        if model is not None:
            self._session.delete(model)
            self._session.commit()

    def _load_department_models(
        self, department_ids: list[int]
    ) -> list[DepartmentModel]:
        if not department_ids:
            return []
        return list(
            self._session.scalars(
                select(DepartmentModel).where(DepartmentModel.id.in_(department_ids))
            ).all()
        )


class SqlAlchemyDepartmentRepository(DepartmentRepository):
    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, department_id: int) -> Department | None:
        model = self._session.get(DepartmentModel, department_id)
        return _to_department(model) if model else None

    def get_by_ids(self, department_ids: list[int]) -> list[Department]:
        if not department_ids:
            return []
        models = self._session.scalars(
            select(DepartmentModel).where(DepartmentModel.id.in_(department_ids))
        ).all()
        return [_to_department(m) for m in models]

    def list_employees(self, department_id: int) -> list[Employee]:
        models = self._session.scalars(
            select(EmployeeModel)
            .join(EmployeeModel.departments)
            .where(DepartmentModel.id == department_id)
            .order_by(EmployeeModel.id)
        ).all()
        return [_to_employee(m, with_departments=False) for m in models]
