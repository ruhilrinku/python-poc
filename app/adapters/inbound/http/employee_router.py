from fastapi import APIRouter, Depends, Response, status

from app.adapters.inbound.http.dependencies import get_employee_service
from app.adapters.inbound.http.presenters import to_employee_out
from app.adapters.inbound.http.schemas import (
    DepartmentsUpdatedOut,
    EmployeeCreateIn,
    EmployeeOut,
    EmployeeUpdateIn,
    MessageOut,
    UpdateDepartmentsIn,
)
from app.application.services import EmployeeService

router = APIRouter(prefix="/api/v1/employees", tags=["employees"])


@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreateIn,
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeOut:
    employee = service.create_employee(
        employee_code=payload.employee_code,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        department_ids=payload.department_ids,
    )
    return to_employee_out(employee)


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeOut:
    return to_employee_out(service.get_employee(employee_id))


@router.put("/{employee_id}", response_model=MessageOut)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdateIn,
    service: EmployeeService = Depends(get_employee_service),
) -> MessageOut:
    service.update_employee(
        employee_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
    )
    return MessageOut(message="Employee updated successfully")


@router.put("/{employee_id}/departments", response_model=DepartmentsUpdatedOut)
def update_employee_departments(
    employee_id: int,
    payload: UpdateDepartmentsIn,
    service: EmployeeService = Depends(get_employee_service),
) -> DepartmentsUpdatedOut:
    employee = service.update_departments(employee_id, payload.department_ids)
    return DepartmentsUpdatedOut(
        message="Departments updated successfully",
        employee_id=employee.id,
        department_ids=[d.id for d in employee.departments],
    )


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
) -> Response:
    service.delete_employee(employee_id)
    # 204 responses carry no body per the HTTP spec.
    return Response(status_code=status.HTTP_204_NO_CONTENT)
