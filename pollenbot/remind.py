"""
Functions for:
- enabling/disabling daily reminders of pollen.
- sending the daily reminder.
"""
import random
import datetime
from telegram.ext import ContextTypes, JobQueue
from .forecast import get_forecast

greetings = [
    "Sup",
    "Hi",
    "Hey",
    "Hello",
    "Howdy",
    "Salutations",
    "Greetings",
    "Yo",
    "What's up",
    "How's it going",
    "Bot here",
]


def _jobname(user: int) -> str:
    return f"reminder-{user}"


def queue_reminder(
    job_queue: JobQueue, user: int, user_data: dict, send_now: bool = False
):
    """Queues a daily reminder for a user.

    Args:
        job_queue (JobQueue): the job queue (usually context.job_queue)
        user (int): user id

    Returns:
        str: "success" if successful, "already_in_queue" if already in queue
    """
    already_a_job = job_queue.get_jobs_by_name(_jobname(user))
    if already_a_job:
        return "already_in_queue"
    job_queue.run_daily(
        _remind,
        time=datetime.time(hour=8, minute=0),
        chat_id=user,
        name=_jobname(user),
        data=user_data,
    )
    if send_now is True:
        job_queue.run_once(
            _remind,
            when=0,
            chat_id=user,
            data=user_data,
        )
    return "success"


def cancel_reminder(job_queue: JobQueue, user: int):
    """Cancels a daily reminder for a user.

    Args:
        job_queue (JobQueue): the job queue (usually context.job_queue)
        user (int): user id

    Returns:
        str: "success" if successful
    """
    jobs = job_queue.get_jobs_by_name(_jobname(user))
    if not jobs:
        return "not_in_queue"
    for job in jobs:
        job.schedule_removal()
    return "success"


_REMINDER_MESSAGE = """
{}! The pollen cometh.

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


def _is_above_threshold(pollen_forecast, threshold):
    # VH > H > M > L
    if pollen_forecast == "VH":
        return True
    elif pollen_forecast == "H" and threshold in ["H", "M", "L"]:
        return True
    elif pollen_forecast == "M" and threshold in ["M", "L"]:
        return True
    elif pollen_forecast == "L" and threshold == "L":
        return True
    else:
        return False


async def _remind(context: ContextTypes.DEFAULT_TYPE):
    """Sends a daily reminder of the pollen, if the threshold is met.

    Args:
        context: the context passed by the job queue

    Raises:
        ValueError: if the user id is not set in the context.job
        ValueError: if the user id is not set in the context
    """
    if context.job is None or context.job.chat_id is None:
        raise ValueError("context.job or context.job.chat_id is None")
    user = context.job.chat_id

    user_data = context.job.data
    region = user_data["region_id"]
    threshold = user_data["threshold"]
    print(f"reminding {user} about {region} with threshold {threshold}")

    greeting = random.choice(greetings)

    forecast = get_forecast()

    region_forecast = next(
        (
            region_forecast
            for region_forecast in forecast
            if region_forecast["id"] == region
        ),
        None,
    )
    if region_forecast is None:
        raise ValueError(f"region {region} not found in forecast")

    region_name = region_forecast["regionName"]
    pollen_levels_symbols = region_forecast["pollenLevel"]
    pollen_levels_words = [
        _convert_pollen_short_to_long(pollen_level)
        for pollen_level in pollen_levels_symbols
    ]

    if _is_above_threshold(pollen_levels_symbols[0], threshold):
        await context.bot.send_message(
            chat_id=user,
            text=_REMINDER_MESSAGE.format(
                greeting,
                region_name,
                pollen_levels_words[0],
                ", ".join(pollen_levels_words[1:]),
            ),
        )
