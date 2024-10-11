from email.mime.text import MIMEText
from smtplib import SMTP
from ssl import create_default_context

from fastapi import BackgroundTasks
from loguru import logger

from app.config import MAIL_HOST, MAIL_PASSWORD, MAIL_PORT, MAIL_USERNAME
from app.core.schemas import UserSchema, UserTransactionSchema


@logger.catch(reraise=True)
def notify_about_action_with_transaction(
        transaction: UserTransactionSchema,
        action_description: str,
        user_changer: UserSchema,
        background_tasks: BackgroundTasks
    ):
    """
    Generates mail text about adding transaction and
    creates background task to send it
    """
    mail_text = (
        f"<h1>Hello, {user_changer.login}</h1>"
        f"<h3>You {action_description} transaction with "
        f"type «<i>{transaction.type_name.name.upper()}</i>» "
        f"in quantity «<i>{transaction.amount}</i>»</h3>"
    )
    background_tasks.add_task(
        send_mail,
        mail_text=mail_text,
        mail_from=user_changer.email,
        mail_to=user_changer.email,
        mail_subj=(
            f"«{transaction.type_name.name.upper()}» transaction "
            f"with ID = {transaction.id} has been {action_description}"))


@logger.catch()
def send_mail(
        mail_text: str, mail_from: str, mail_to: str, mail_subj: str
    ):
    """
    Connects to SMTP server and
    sends message through it to specified email
    """
    message = MIMEText(mail_text, "html")
    message["From"] = mail_from
    message["To"] = mail_to
    message["Subject"] = mail_subj

    if all((MAIL_HOST, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD)):
        with SMTP(MAIL_HOST, MAIL_PORT) as mail_server:
            mail_server.ehlo()
            mail_server.starttls(context=create_default_context())
            mail_server.ehlo()
            mail_server.login(MAIL_USERNAME, MAIL_PASSWORD)
            mail_server.send_message(message)
            mail_server.quit()

        logger.info(f"Mail sended to {mail_to} successfully!")
    else:
        logger.info(
            f"Mail with text:\n'''\n{mail_text}\n'''\n "
            f"should be sent to {mail_to}")
