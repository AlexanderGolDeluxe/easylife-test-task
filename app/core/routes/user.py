from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import API_PREFIX
from app.configuration.db_helper import db_helper
from app.core.crud.user import (
    create_user, delete_user, get_users, validate_creating_user
)
from app.core.routes.auth import RoleChecker, get_current_auth_user
from app.core.schemas import UserCreate, UserSchema

router = APIRouter(prefix=API_PREFIX + "/user", tags=["user"])


@router.post("/add", response_model=UserSchema, status_code=201)
async def add_user(
        user_in: UserCreate = Depends(validate_creating_user),
        session: AsyncSession = Depends(
            db_helper.scoped_session_dependency)):

    return await create_user(session, user_in)


@router.delete("/remove", response_model=UserSchema)
async def remove_user(
        user_id: int = Form(ge=1),
        user: UserSchema = Depends(RoleChecker({"Owner", "Admin"})),
        session: AsyncSession = Depends(
            db_helper.scoped_session_dependency)):

    return await delete_user(session, user_id, user)


@router.get("/details", response_model=UserSchema)
async def get_user(
        user: UserSchema = Depends(get_current_auth_user)):

    return user


@router.get("/all", response_model=list[UserSchema])
async def get_all_users(
        user: UserSchema = Depends(RoleChecker({"Owner", "Admin"})),
        session: AsyncSession = Depends(
            db_helper.scoped_session_dependency)):

    return await get_users(session)
