from telegram import Update
from telegram.ext import CommandHandler

_HELP_MESSAGE = """
Use /start to set up, or /forecast to get the forecast for your region.

This bot pulls data from the Met Office pollen forecast:
https://www.metoffice.gov.uk/weather/warnings-and-advice/seasonal-advice/pollen-forecast

Privacy:
Naturally, I store your region and preferences. If you use /start and choose not to set up the bot, this information will be deleted.

If you have any problems or suggestions, you can text me! @alifeeerenn

Author: alifeee
Code on GitHub:
https://github.com/alifeee/pollen_bot
"""


async def _help(update: Update, _) -> None:
    """Handle /help."""
    if update.message:
        await update.message.reply_text(_HELP_MESSAGE)


help_handler = CommandHandler("help", _help)
