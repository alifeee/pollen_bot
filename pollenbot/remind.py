"""
Functions for:
- enabling/disabling daily reminders of pollen.
- sending the daily reminder.
"""
import random
import datetime
from telegram.ext import ContextTypes, JobQueue
from .forecast import PollenLevel, get_forecast_for_region, get_forecasts

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


def _is_above_threshold(pollen_level: PollenLevel, threshold: PollenLevel) -> bool:
    # VH > H > M > L
    if pollen_level == PollenLevel.VERY_HIGH:
        return True
    if pollen_level == PollenLevel.HIGH and threshold in [
        PollenLevel.HIGH,
        PollenLevel.MEDIUM,
        PollenLevel.LOW,
    ]:
        return True
    if pollen_level == PollenLevel.MEDIUM and threshold in [
        PollenLevel.MEDIUM,
        PollenLevel.LOW,
    ]:
        return True
    if pollen_level == PollenLevel.LOW and threshold == PollenLevel.LOW:
        return True
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

    user_data: dict = context.job.data
    region_id = user_data["region_id"]
    threshold = user_data["threshold"]

    if region_id is None:
        raise ValueError("region is None")
    if threshold is None:
        raise ValueError("threshold is None")

    greeting = random.choice(greetings)

    forecasts = get_forecasts()
    forecast = get_forecast_for_region(forecasts, region_id)
    if forecast is None:
        raise ValueError(f"forecast for region {region_id} is None")
    try:
        today_forecast = forecast.days[0]
    except IndexError as error:
        raise ValueError("forecast is empty") from error

    if _is_above_threshold(today_forecast.pollen_level, threshold):
        await context.bot.send_message(
            chat_id=user,
            text=_REMINDER_MESSAGE.format(
                greeting,
            ),
        )
