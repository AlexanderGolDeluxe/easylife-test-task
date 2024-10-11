from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.models import TransactionType, User, UserTransaction
from app.core.schemas import UserSchema, UserTransactionCreate
from app.utils.work_with_dates import parse_like_date


@logger.catch(reraise=True)
async def get_transaction_type_id(session: AsyncSession, type_name: str):
    """
    Retrieves transaction type ID from DB using specified `type name`
    """
    transaction_type_id = await session.scalar(
        select(TransactionType.id)
        .where(func.lower(TransactionType.name) == type_name.lower())
    )
    if not transaction_type_id:
        await session.close()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Transaction type with name = «{type_name}» not found"))

    return transaction_type_id


@logger.catch(reraise=True)
async def get_transaction_by_id(
        session: AsyncSession, transaction_id: int
    ):
    """
    Retrieves record about transaction from DB
    using specified `transaction id`
    """
    stmt = (
        select(UserTransaction)
        .where(UserTransaction.id == transaction_id)
        .options(joinedload(UserTransaction.type_name))
        .options(
            joinedload(UserTransaction.created_by)
            .options(
                joinedload(User.role),
                joinedload(User.created_transactions))))

    transaction_row = await session.scalar(stmt)
    if not transaction_row:
        await session.close()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Transaction with ID = «{transaction_id}» not found")

    return transaction_row


@logger.catch(reraise=True)
async def generate_transaction(
        session: AsyncSession,
        transaction_in: UserTransactionCreate,
        created_by: UserSchema
    ):
    """
    Validates transaction data from user,
    calculates remaining fields and generates the transaction,
    after that saving it in database
    """
    created_transaction = UserTransaction(
        amount=transaction_in.amount,
        transaction_type_id=(
            await get_transaction_type_id(
                session, transaction_in.type_name)
        ),
        created_by_id=created_by.id
    )
    session.add(created_transaction)
    await session.commit()
    created_transaction_schema = await get_transaction_by_id(
        session, created_transaction.id)

    return created_transaction_schema


@logger.catch(reraise=True)
async def delete_transaction(session: AsyncSession, transaction_id: int):
    """
    Deletes transaction from DB by specified ID and returns its object
    """
    transaction_schema = await get_transaction_by_id(
        session, transaction_id
    )
    await session.delete(transaction_schema)
    await session.commit()

    return transaction_schema


@logger.catch(reraise=True)
async def get_all_transactions(session: AsyncSession, user: UserSchema):
    """Executes query to retrieve all transactions from database"""
    stmt = (
        select(UserTransaction)
        .options(joinedload(UserTransaction.type_name))
        .options(
            joinedload(UserTransaction.created_by)
            .options(
                joinedload(User.role),
                joinedload(User.created_transactions))
        )
        .order_by(UserTransaction.created_at))

    if user is not None and user.role.position == "User":
        stmt = stmt.where(UserTransaction.created_by_id == user.id)

    return (await session.scalars(stmt)).unique().all()


@logger.catch(reraise=True)
async def get_all_transactions_for_view(
        session: AsyncSession, creation_date: str | None = None
    ):
    """
    Retrieves all transactions from database to represent in view.
    Also allows to query transactions with a specific `creation date`
    """
    stmt = (
        select(UserTransaction)
        .options(joinedload(UserTransaction.type_name))
        .options(
            joinedload(UserTransaction.created_by)
            .options(
                joinedload(User.role),
                joinedload(User.created_transactions))
        )
        .order_by(UserTransaction.created_at)
    )
    if creation_date:
        stmt = stmt.where(
            func.date(UserTransaction.created_at) ==
            parse_like_date(creation_date))

    return (await session.scalars(stmt)).unique().all()
