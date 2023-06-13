"""/start"""
from telegram import Update
from telegram.ext import CommandHandler

_START_MESSAGE = """
Achoo!
"""


async def _start(update: Update, _) -> None:
    if update.message is not None:
        await update.message.reply_text(_START_MESSAGE)


start_handler = CommandHandler("start", _start)
