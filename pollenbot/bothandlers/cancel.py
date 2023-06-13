"""cancel current conversation"""
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ConversationHandler, CommandHandler

_CANCEL_MESSAGE = """
Ok, cancelled.
"""


async def _cancel(update: Update, _) -> int:
    """cancel current conversation"""
    if update.message:
        await update.message.reply_text(
            _CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove()
        )
    return ConversationHandler.END


cancel_handler = CommandHandler("cancel", _cancel)
