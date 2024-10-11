from fastapi import Form, HTTPException, status
from loguru import logger

from app.config import TRANSACTION_TYPES


@logger.catch(reraise=True)
def check_transaction_type(transaction_name: str = Form(
        examples=["CREATE"], description=(
            f"Choose one of this: «{'», «'.join(TRANSACTION_TYPES)}»")
    )):
    """
    Validates accordance
    between user input of `transaction name` and supported types
    """
    if not transaction_name.upper() in set(TRANSACTION_TYPES):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Transaction type name must be one of: "
                f"«{'», «'.join(TRANSACTION_TYPES)}»"))

    return transaction_name
