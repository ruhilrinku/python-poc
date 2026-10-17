class DomainError(Exception):
    """Base class for domain-level errors mapped to API error responses."""

    code = "DOMAIN_ERROR"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ValidationError(DomainError):
    code = "VALIDATION_ERROR"


class EmployeeNotFound(DomainError):
    code = "EMPLOYEE_NOT_FOUND"


class DepartmentNotFound(DomainError):
    code = "DEPARTMENT_NOT_FOUND"


class DuplicateEmail(DomainError):
    code = "DUPLICATE_EMAIL"


class DuplicateEmployeeCode(DomainError):
    code = "DUPLICATE_EMPLOYEE_CODE"
