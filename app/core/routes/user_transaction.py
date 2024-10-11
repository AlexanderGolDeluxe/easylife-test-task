from fastapi import APIRouter, BackgroundTasks, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import API_PREFIX
from app.configuration.db_helper import db_helper
from app.core.crud.user_transaction import (
    delete_transaction,
    generate_transaction,
    get_all_transactions
)
from app.core.routes.auth import RoleChecker, get_current_auth_user
from app.core.schemas import (
    UserSchema, UserTransactionCreate, UserTransactionSchema
)
from app.utils.email_sender import notify_about_action_with_transaction

router = APIRouter(
    prefix=API_PREFIX + "/transaction", tags=["transaction"])


@router.post(
        "/add", response_model=UserTransactionSchema, status_code=201)
async def add_transaction(
        transaction_in: UserTransactionCreate,
        background_tasks: BackgroundTasks,
        user: UserSchema = Depends(RoleChecker({"Admin", "User"})),
        session: AsyncSession = Depends(
            db_helper.scoped_session_dependency)):
    created_transaction = await generate_transaction(
        session, transaction_in, user
    )
    if created_transaction:
        notify_about_action_with_transaction(
            created_transaction, "added", user, background_tasks)

    return created_transaction


@router.delete("/remove", response_model=UserTransactionSchema)
async def remove_transaction(
        background_tasks: BackgroundTasks,
        transaction_id: int = Form(ge=1),
        user: UserSchema = Depends(RoleChecker({"Admin"})),
        session: AsyncSession = Depends(
            db_helper.scoped_session_dependency)):
    deleted_transaction = await delete_transaction(
        session, transaction_id
    )
    if deleted_transaction:
        notify_about_action_with_transaction(
            deleted_transaction, "deleted", user, background_tasks)

    return deleted_transaction


@router.get("/retrieve", response_model=list[UserTransactionSchema])
async def get_transactions(
        user: UserSchema = Depends(get_current_auth_user),
        session: AsyncSession = Depends(
            db_helper.scoped_session_dependency)):

    return await get_all_transactions(session, user)
