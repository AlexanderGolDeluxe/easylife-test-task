from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ROLE_PERMISSIONS, TRANSACTION_TYPES
from app.configuration.db_helper import db_helper
from app.core.models import RolePermission, TransactionType
from app.core.schemas import RolePermissionCreate, TransactionTypeCreate


@logger.catch(reraise=True)
async def insert_role_permissions(session: AsyncSession):
    """Add initial role permissions to DB"""
    stmt = select(RolePermission.position)
    existing_permissions = {
        row[0] for row in (await session.execute(stmt))
    }
    necessary_permissions = {
        role: desc for role, desc in ROLE_PERMISSIONS.items()
        if not role in existing_permissions
    }
    if necessary_permissions:
        session.add_all(
            RolePermission(**RolePermissionCreate(
                position=role, description_of_access_to_actions=desc
            ).model_dump())
            for role, desc in necessary_permissions.items()
        )
        await session.commit()


@logger.catch(reraise=True)
async def insert_transaction_types(session: AsyncSession):
    """Add initial transaction types to DB"""
    stmt = select(TransactionType.name)
    existing_types = {
        row[0] for row in (await session.execute(stmt))
    }
    necessary_types = tuple(filter(
        lambda type_name: not type_name in existing_types,
        TRANSACTION_TYPES
    ))
    if necessary_types:
        session.add_all(
            TransactionType(
                **TransactionTypeCreate(name=type_name).model_dump())
            for type_name in necessary_types
        )
        await session.commit()


@logger.catch(reraise=True)
async def insert_all_initial_db_data():
    """
    Fill DB with initial data for correct functioning of app
    """
    session = db_helper.get_scoped_session()
    await insert_role_permissions(session)
    await insert_transaction_types(session)
    await session.close()
