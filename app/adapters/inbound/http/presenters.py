from app.adapters.inbound.http.schemas import (
    DepartmentOut,
    EmployeeOut,
    EmployeeSummaryOut,
)
from app.domain.entities import Employee


def to_employee_out(employee: Employee) -> EmployeeOut:
    return EmployeeOut(
        id=employee.id,
        employee_code=employee.employee_code,
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        departments=[
            DepartmentOut(id=d.id, name=d.name) for d in employee.departments
        ],
    )


def to_employee_summary(employee: Employee) -> EmployeeSummaryOut:
    return EmployeeSummaryOut(
        id=employee.id,
        employee_code=employee.employee_code,
        first_name=employee.first_name,
        last_name=employee.last_name,
    )
