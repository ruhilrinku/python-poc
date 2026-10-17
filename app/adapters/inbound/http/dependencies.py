from fastapi import Depends
from sqlalchemy.orm import Session

from app.adapters.outbound.persistence.repositories import (
    SqlAlchemyDepartmentRepository,
    SqlAlchemyEmployeeRepository,
)
from app.application.services import EmployeeService
from app.infrastructure.database import get_session

def get_employee_service(
    session: Session = Depends(get_session),
) -> EmployeeService:
    return EmployeeService(
        employees=SqlAlchemyEmployeeRepository(session),
        departments=SqlAlchemyDepartmentRepository(session),
    )
