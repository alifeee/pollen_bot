"""/start"""
from telegram import Update
from telegram import *
from telegram.ext import CommandHandler
from telegram.ext import *
from .cancel import cancel_handler
from ..forecast import PollenLevel, Region

(
    USER_CONFIRMING_USE,
    USER_CHOOSING_REGION,
    USER_CONFIRMING_REMINDERS,
    USER_CHOOSING_THRESHOLD,
) = range(4)

_START_MESSAGE = """
Achoo! I am a sage. I know all about pollen, thanks to my friend, Metfeld Officeton Esq.
Would you like me to tell you about the pollen forecast?
"""

_INITIALISE_OPTION = """
Let's do it!
"""

_DO_NOT_INITIALISE_OPTION = """
Another time...
"""

_INITIALISE_MESSAGE = (
    _START_MESSAGE
    + """
Great! What region are you in?
"""
)

_DO_NOT_INITIALISE_MESSAGE = """
okay :(
use /start to try again when you're ready
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

_THRESHOLD_OPTIONS = {
    "Medium": PollenLevel.MEDIUM,
    "High": PollenLevel.HIGH,
    "Very High": PollenLevel.VERY_HIGH,
}

_THRESHOLD_MESSAGE = """
Radical. I'll text you at 9am whenever the pollen count is {} or above.
You can also always use /forecast to check the next few days :)
"""


async def _start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None:
        raise ValueError("Update message should not be none")
    regions: list[Region] = context.bot_data["regions"]
    await update.message.reply_text(
        _START_MESSAGE,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        _INITIALISE_OPTION, callback_data=_INITIALISE_OPTION
                    )
                ],
                [
                    InlineKeyboardButton(
                        _DO_NOT_INITIALISE_OPTION,
                        callback_data=_DO_NOT_INITIALISE_OPTION,
                    )
                ],
            ]
        ),
    )
    return USER_CONFIRMING_USE


async def _confirm_use(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query is None:
        raise ValueError("Update callback query should not be none")

    query = update.callback_query
    await query.answer()

    if query.data == _INITIALISE_OPTION:
        regions: list[Region] = context.bot_data["regions"]
        await query.edit_message_text(
            _INITIALISE_MESSAGE,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(region.name, callback_data=region.id)]
                    for region in regions
                ]
            ),
        )
        return USER_CHOOSING_REGION

    if query.data == _DO_NOT_INITIALISE_OPTION:
        await query.edit_message_text(_DO_NOT_INITIALISE_MESSAGE)
        return ConversationHandler.END

    else:
        raise ValueError(f"Unrecognized option {query.data}")


async def _confirm_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query is None:
        raise ValueError("Update callback query should not be none")

    query = update.callback_query
    await query.answer()

    regions: list[Region] = context.bot_data["regions"]
    user_region_id = query.data
    user_region = next(
        (region for region in regions if region.id == user_region_id), None
    )
    if user_region is None:
        raise ValueError(f"Region ID {user_region_id} not found in regions")
    if context.user_data is None:
        context.user_data = {}
    context.user_data["region"] = user_region

    await query.edit_message_text(
        _REMINDERS_MESSAGE.format(f"{user_region.id}, {user_region.name}"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(_YES_OPTION, callback_data=_YES_OPTION),
                    InlineKeyboardButton(_NO_OPTION, callback_data=_NO_OPTION),
                ]
            ]
        ),
    )
    return USER_CONFIRMING_REMINDERS


async def _confirm_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query is None:
        raise ValueError("Update query should not be none")

    query = update.callback_query
    await query.answer()

    if query.data == _NO_OPTION:
        if context.user_data is None:
            context.user_data = {}
        context.user_data["reminders"] = False
        await query.edit_message_text(_NO_MESSAGE)
        return ConversationHandler.END

    elif query.data == _YES_OPTION:
        if context.user_data is None:
            context.user_data = {}
        context.user_data["reminders"] = True

        await query.edit_message_text(
            _YES_MESSAGE,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(threshold_text, callback_data=threshold_text)]
                    for threshold_text in _THRESHOLD_OPTIONS.keys()
                ]
            ),
        )
        return USER_CHOOSING_THRESHOLD

    else:
        raise ValueError(f"Unrecognized option {query.data}")


async def _confirm_threshold(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query is None:
        raise ValueError("Update query should not be none")

    query = update.callback_query
    await query.answer()

    desired_threshold_text = query.data
    if desired_threshold_text is None:
        raise ValueError("Callback query data should not be none")

    desired_threshold = _THRESHOLD_OPTIONS[desired_threshold_text]

    if context.user_data is None:
        context.user_data = {}
    context.user_data["threshold"] = desired_threshold

    await query.edit_message_text(_THRESHOLD_MESSAGE.format(desired_threshold))
    return ConversationHandler.END


start_handler = ConversationHandler(
    entry_points=[CommandHandler("start", _start)],
    states={
        USER_CONFIRMING_USE: [CallbackQueryHandler(_confirm_use)],
        USER_CHOOSING_REGION: [CallbackQueryHandler(_confirm_region)],
        USER_CONFIRMING_REMINDERS: [
            CallbackQueryHandler(_confirm_reminders),
        ],
        USER_CHOOSING_THRESHOLD: [
            CallbackQueryHandler(_confirm_threshold),
        ],
    },
    fallbacks=[cancel_handler],
)
