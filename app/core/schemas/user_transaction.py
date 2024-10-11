from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field, NonNegativeInt

from app.config import TRANSACTION_TYPES
from app.core.schemas import UserSchema
from app.core.schemas.validators import check_transaction_type


class TransactionTypeCreate(BaseModel):
    name: str


class TransactionTypeSchema(TransactionTypeCreate):
    id: int


class UserTransactionCreate(BaseModel):
    type_name: Annotated[
        str,
        Field(examples=TRANSACTION_TYPES),
        BeforeValidator(check_transaction_type)
    ]
    amount: NonNegativeInt = 1


class UserTransactionRead(UserTransactionCreate):
    id: int
    type_name: TransactionTypeSchema
    created_at: datetime


class UserTransactionSchema(UserTransactionRead):
    created_by: UserSchema
