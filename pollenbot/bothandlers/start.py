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
Thanks! You've set your region to:
{}

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
_THRESHOLD_CORRESPONDS_TO = ["M", "H", "VH"]

_THRESHOLD_MESSAGE = """
Radical. I'll text you at 9am whenever the pollen count is {} or above.
You can also always use /forecast to check the next few days :)
"""


async def _start(update: Update, _) -> int:
    if update.message is not None:
        await update.message.reply_text(_START_MESSAGE)
        return USER_CHOOSING_REGION

    raise ValueError("Update message should not be none")


async def _confirm_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is not None:
        # dict with regionName and id
        allowed_regions = context.bot_data["regions"]

        sent_region = update.message.text
        for region in allowed_regions:
            if sent_region in (region["regionName"], region["id"]):
                set_region = region["id"]
                if context.user_data is None:
                    context.user_data = {}
                context.user_data["region_id"] = set_region

                await update.message.reply_text(
                    _REMINDERS_MESSAGE.format(f"{region['id']}, {region['regionName']}")
                )
                return USER_CONFIRMING_REMINDERS

        await update.message.reply_text(
            f"Sorry, I don't know a region by the name:\n{update.message.text}."
        )
        return USER_CHOOSING_REGION

    raise ValueError("Update message should not be none")


async def _no_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is not None:
        if context.user_data is None:
            context.user_data = {}
        context.user_data["reminders"] = False

        await update.message.reply_text(_NO_MESSAGE)
        return ConversationHandler.END

    raise ValueError("Update message should not be none")


async def _confirm_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is not None:
        if context.user_data is None:
            context.user_data = {}
        context.user_data["reminders"] = True

        await update.message.reply_text(_YES_MESSAGE)
        return USER_CHOOSING_THRESHOLD

    raise ValueError("Update message should not be none")


async def _confirm_threshold(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is not None:
        desired_threshold = update.message.text
        if desired_threshold not in _THRESHOLD_OPTIONS:
            await update.message.reply_text(
                f"Sorry, I don't know a threshold by the name:\n{update.message.text}."
            )
            return USER_CHOOSING_THRESHOLD

        if context.user_data is None:
            context.user_data = {}
        context.user_data["threshold"] = _THRESHOLD_CORRESPONDS_TO[
            _THRESHOLD_OPTIONS.index(desired_threshold)
        ]

        await update.message.reply_text(_THRESHOLD_MESSAGE.format(desired_threshold))
        return ConversationHandler.END

    raise ValueError("Update message should not be none")


start_handler = ConversationHandler(
    entry_points=[CommandHandler("start", _start)],
    states={
        USER_CHOOSING_REGION: [MessageHandler(filters.TEXT, _confirm_region)],
        USER_CONFIRMING_REMINDERS: [
            MessageHandler(filters.Regex(f"^{_YES_OPTION}$"), _confirm_reminders),
            MessageHandler(filters.Regex(f"^{_NO_OPTION}$"), _no_reminders),
        ],
        USER_CHOOSING_THRESHOLD: [
            MessageHandler(filters.TEXT, _confirm_threshold),
        ],
    },
    fallbacks=[cancel_handler],
)
