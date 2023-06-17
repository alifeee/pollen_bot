"""/forecast"""
from telegram import Update
from telegram import *
from telegram.ext import *
from ..forecast import (
    Forecast,
    color_pollen_level,
    get_forecasts,
    format_pollen_level,
    get_forecast_for_region,
)
import datetime

_FORECAST_MESSAGE = """
Today's pollen forecast in {}:

{}

The rest of the week:

{}

To turn off updates, or change your threshold, use /start.
"""


def get_forecast_message(forecast: Forecast) -> str:
    """Get the forecast message for a region.

    Args:
        region_id (str): Region ID

    Raises:
        ValueError: If region ID is not found in forecasts

    Returns:
        str: Forecast message
    """

    region_name = forecast.region.name
    days = forecast.days
    pollen_levels = [format_pollen_level(day.pollen_level) for day in days]
    pollen_indicators = [color_pollen_level(day.pollen_level) for day in days]
    days_names = [day.date.strftime("%A") for day in days]

    return _FORECAST_MESSAGE.format(
        region_name,
        f"{pollen_indicators[0]} {pollen_levels[0]}",
        "\n".join(
            [
                f"{indicator} {day_name}: {pollen_level}"
                for indicator, day_name, pollen_level in zip(
                    pollen_indicators[1:], days_names[1:], pollen_levels[1:]
                )
            ]
        ),
    )


async def _forecast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        raise ValueError("Update message should not be none")

    region = context.user_data.get("region", None)
    if region is None:
        await update.message.reply_text("No region set! Use /start")
        return

    forecasts = get_forecasts()
    region_forecast = get_forecast_for_region(forecasts, region.id)
    if region_forecast is None:
        await update.message.reply_text("Region not found! Try /start")
        return

    await update.message.reply_text(get_forecast_message(region_forecast))


forecast_handler = CommandHandler("forecast", _forecast)
