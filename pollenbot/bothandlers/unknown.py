"""Handle unknown commands."""
from telegram import Update
from telegram.ext import MessageHandler, filters

_COMMAND_UNKOWN_MESSAGE = """
That's not a command I know!
"""


async def _unknown(update: Update, _) -> None:
    """Handle unknown commands."""
    if update.message:
        await update.message.reply_text(_COMMAND_UNKOWN_MESSAGE)


unknown_command_handler = MessageHandler(filters.COMMAND, _unknown)
