"""Error handler: sends "admin" a message with the error and the update that caused it."""
import os
import logging
from telegram.ext import ContextTypes


async def error_handler(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends traceback to admin."""
    bot = context.bot
    try:
        admin_id = os.environ["ADMIN_USER_ID"]
    except KeyError as error:
        raise ValueError("ADMIN_USER_ID environment variable not set.") from error
    try:
        user = update.effective_user
        chat = update.effective_chat
    except AttributeError:
        user = "unknown"
        chat = "unknown"
    await bot.send_message(
        chat_id=admin_id,
        text=f"""
Error!

User: {user}

Chat: {chat}

Update: {update}

Error: {context.error}
        """,
    )
    print(context)
    logger = logging.getLogger(__name__)
    logger.error("Update %s caused error %s", update.update_id, context.error)
    # raise context.error
