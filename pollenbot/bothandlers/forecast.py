"""/forecast"""
from telegram import Update
from telegram import *
from telegram.ext import *
from ..forecast import Forecast, get_forecasts, format_pollen_level
import datetime

_FORECAST_MESSAGE = """
Today's pollen forecast in {}:
{}

The rest of the week:
{}
"""


def get_forecast_message(forecasts: list[Forecast], region_id: str) -> str:
    """Get the forecast message for a region.

    Args:
        region_id (str): Region ID

    Raises:
        ValueError: If region ID is not found in forecasts

    Returns:
        str: Forecast message
    """
    region_forecast = next(
        (
            reg_forecast
            for reg_forecast in forecasts
            if reg_forecast.region.id == region_id
        ),
        None,
    )
    if region_forecast is None:
        raise ValueError(f"Region {region_id} not found in forecast")

    region_name = region_forecast.region.name
    days = region_forecast.days
    pollen_levels = [format_pollen_level(day.pollen_level) for day in days]
    days_names = [day.date.strftime("%A") for day in days]

    return _FORECAST_MESSAGE.format(
        region_name,
        pollen_levels[0],
        "\n".join(
            [
                f"{day_name}: {pollen_level}"
                for day_name, pollen_level in zip(days_names[1:], pollen_levels[1:])
            ]
        ),
    )


async def _forecast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        raise ValueError("Update message should not be none")

    if context.user_data is None:
        context.user_data = {}
    region_id = context.user_data.get("region_id", None)
    if region_id is None:
        await update.message.reply_text("No region set! Use /start")
        return

    forecasts = get_forecasts()
    await update.message.reply_text(get_forecast_message(forecasts, region_id))


forecast_handler = CommandHandler("forecast", _forecast)
