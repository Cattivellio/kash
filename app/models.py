from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class UserOut(BaseModel):
    id: int
    name: str
    locale: str
    theme: str
    created_at: str


class UserPrefs(BaseModel):
    locale: str = "es"
    theme: str = "light"


class RecordCreate(BaseModel):
    kind: Literal["income", "expense"]
    name: str = Field(..., min_length=1, max_length=200)
    occurred_at: str = Field(..., description="ISO datetime")
    amount: float = Field(..., gt=0)
    payment_method: Literal["cash", "card", "zelle"]
    note: str = ""


class RecordUpdate(BaseModel):
    kind: Literal["income", "expense"] | None = None
    name: str | None = Field(None, min_length=1, max_length=200)
    occurred_at: str | None = None
    amount: float | None = Field(None, gt=0)
    payment_method: Literal["cash", "card", "zelle"] | None = None
    note: str | None = None


class RecordOut(BaseModel):
    id: int
    user_id: int
    kind: str
    name: str
    occurred_at: str
    amount: float
    payment_method: str
    note: str
    created_at: str
    updated_at: str


class MonthSummary(BaseModel):
    income: float
    expense: float
    balance: float


class HealthResponse(BaseModel):
    ok: bool
    db: bool
    now: datetime
