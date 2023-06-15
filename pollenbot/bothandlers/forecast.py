"""/forecast"""
from telegram import Update
from telegram import *
from telegram.ext import *
from ..forecast import get_forecast

_FORECAST_MESSAGE = """
Today's pollen forecast in {}:
{}

The rest of the week:
{}
"""


def _convert_pollen_short_to_long(short_pollen):
    if short_pollen == "L":
        return "Low"
    elif short_pollen == "M":
        return "Medium"
    elif short_pollen == "H":
        return "High"
    elif short_pollen == "VH":
        return "Very High"
    else:
        return "error"


async def _forecast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        raise ValueError("Update message should not be none")

    if context.user_data is None:
        context.user_data = {}
    region_id = context.user_data.get("region_id", None)
    if region_id is None:
        await update.message.reply_text("No region set! Use /start")
        return
    forecast = get_forecast()
    region_forecast = next(
        (reg_forecast for reg_forecast in forecast if reg_forecast["id"] == region_id),
        None,
    )
    if region_forecast is None:
        raise ValueError(f"Region {region_id} not found in forecast")

    region_name = region_forecast["regionName"]
    pollen_levels_symbols = region_forecast["pollenLevel"]
    pollen_levels_words = [
        _convert_pollen_short_to_long(pollen_level)
        for pollen_level in pollen_levels_symbols
    ]

    await update.message.reply_text(
        _FORECAST_MESSAGE.format(
            region_name,
            pollen_levels_words[0],
            ", ".join(pollen_levels_words[1:]),
        ),
    )


forecast_handler = CommandHandler("forecast", _forecast)
