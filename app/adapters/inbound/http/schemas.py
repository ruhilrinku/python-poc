from pydantic import BaseModel, EmailStr, Field


class DepartmentOut(BaseModel):
    id: int
    name: str


class EmployeeCreateIn(BaseModel):
    employee_code: str = Field(min_length=1)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: EmailStr
    phone: str | None = None
    department_ids: list[int] = Field(default_factory=list)


class EmployeeUpdateIn(BaseModel):
    first_name: str | None = Field(default=None, min_length=1)
    last_name: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = None
    phone: str | None = None


class UpdateDepartmentsIn(BaseModel):
    department_ids: list[int]


class EmployeeOut(BaseModel):
    id: int
    employee_code: str
    first_name: str
    last_name: str
    email: str
    departments: list[DepartmentOut] = Field(default_factory=list)


class EmployeeSummaryOut(BaseModel):
    id: int
    employee_code: str
    first_name: str
    last_name: str


class DepartmentEmployeesOut(BaseModel):
    department_id: int
    department_name: str
    employees: list[EmployeeSummaryOut]


class MessageOut(BaseModel):
    message: str


class DepartmentsUpdatedOut(BaseModel):
    message: str
    employee_id: int
    department_ids: list[int]
