"""start the bot!"""
import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import *
from telegram.ext import *
from pollenbot.forecast import get_regions
from pollenbot.bothandlers.start import start_handler
from pollenbot.bothandlers.unknown import unknown_command_handler
from pollenbot.bothandlers.error import error_handler
from pollenbot.remind import queue_reminder

load_dotenv()
try:
    API_KEY = os.environ["TELEGRAM_BOT_ACCESS_TOKEN"]
except KeyError as e:
    raise ValueError(
        "Please set the environment variable TELEGRAM_BOT_ACCESS_TOKEN"
    ) from e

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """start the bot!"""
    persistent_data = PicklePersistence(
        filepath="bot_data.pickle",
        store_data=PersistenceInput(user_data=True, bot_data=False),
    )
    loop = asyncio.new_event_loop()
    all_user_data = loop.run_until_complete(persistent_data.get_user_data())
    logger.info("Loaded user data: %s", all_user_data)
    loop.close()

    async def add_regions_to_application(application: Application) -> None:
        application.bot_data["regions"] = get_regions()

    application = (
        Application.builder()
        .token(API_KEY)
        .persistence(persistent_data)
        .post_init(add_regions_to_application)
        .build()
    )

    application.add_handler(start_handler)

    application.add_handler(unknown_command_handler)
    application.add_error_handler(error_handler)

    for user_id, user_data in all_user_data.items():
        try:
            reminders_on = user_data["reminders"]
        except KeyError:
            continue
        if reminders_on:
            if application.job_queue is None:
                raise ValueError("Job queue not set in application")
            queue_reminder(
                application.job_queue,
                user_id,
                user_data=user_data,
                send_now=True,
            )

    _ = application.bot.set_my_commands(
        [
            BotCommand("start", "Setup region/reminders"),
            BotCommand("forecast", "Show this week's forecast"),
            BotCommand("cancel", "Cancel current operation"),
        ]
    )

    application.run_polling()


if __name__ == "__main__":
    main()
