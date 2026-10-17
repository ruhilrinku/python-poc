from fastapi import APIRouter, Depends

from app.adapters.inbound.http.dependencies import get_employee_service
from app.adapters.inbound.http.presenters import to_employee_summary
from app.adapters.inbound.http.schemas import DepartmentEmployeesOut
from app.application.services import EmployeeService

router = APIRouter(prefix="/api/v1/departments", tags=["departments"])

@router.get("/{department_id}/employees", response_model=DepartmentEmployeesOut)
def get_department_employees(
    department_id: int,
    service: EmployeeService = Depends(get_employee_service),
) -> DepartmentEmployeesOut:
    department, employees = service.get_employees_by_department(department_id)
    return DepartmentEmployeesOut(
        department_id=department.id,
        department_name=department.name,
        employees=[to_employee_summary(e) for e in employees],
    )
