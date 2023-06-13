"""/start"""
from telegram import Update
from telegram import *
from telegram.ext import CommandHandler
from telegram.ext import *
from .cancel import cancel_handler

USER_CHOOSING_REGION = 0
USER_CONFIRMING_REMINDERS = 1
USER_CHOOSING_THRESHOLD = 2

_START_MESSAGE = """
Achoo! I am a sage. I know all about pollen, thanks to my friend, Metfeld Officeton Esq.
Let me know what region you're in and I can give you some forecasts!
"""

_REMINDERS_MESSAGE = """
Thanks!
Would you like me to text you whenever the pollen count is high near you?
(above your chosen threshold)
"""

_YES_OPTION = "Yes"

_NO_OPTION = "No"

_NO_MESSAGE = """
Well. Okay. You can still look up the forecast with /forecast.
"""

_YES_MESSAGE = """
Super! What threshold would you like to set?
"""

_THRESHOLD_OPTIONS = ["Medium", "High", "Very High"]

_THRESHOLD_MESSAGE = """
Radical. I'll text you at 9am whenever the pollen count is {} or above.
You can also always use /forecast to check the next few days :)
"""


async def _start(update: Update, _) -> None:
    if update.message is not None:
        await update.message.reply_text(_START_MESSAGE)


start_handler = ConversationHandler(
    entry_points=[CommandHandler("start", _start)],
    states={
        # USER_CHOOSING_REGION:
        # USER_CONFIRMING_REMINDERS:
        # USER_CHOOSING_THRESHOLD:
    },
    fallbacks=[cancel_handler],
)
