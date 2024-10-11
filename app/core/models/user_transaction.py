from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base

if TYPE_CHECKING:
    from app.core.models import User


class TransactionType(Base):
    __tablename__ = "transaction_type"

    name: Mapped[str]


class UserTransaction(Base):
    __tablename__ = "user_transaction"

    transaction_type_id: Mapped[int] = mapped_column(
        ForeignKey("transaction_type.id")
    )
    type_name: Mapped[TransactionType] = relationship()
    amount: Mapped[int] = mapped_column(
        CheckConstraint("amount > 0"), default=1, server_default="1"
    )
    created_by_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created_by: Mapped["User"] = relationship(
        back_populates="created_transactions"
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
