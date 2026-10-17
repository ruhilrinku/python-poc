from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Department:
    id: int | None
    department_code: str
    name: str
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Employee:
    id: int | None
    employee_code: str
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    departments: list[Department] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
