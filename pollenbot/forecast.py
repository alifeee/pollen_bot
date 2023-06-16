"""Methods to grab pollen forecasts from the Met Office website.
Currently, the API doesn't support this, so we do some cheeky scraping.
"""
import re
from enum import Enum
import datetime
import json
import requests

POLLEN_FORECAST_URL = "https://www.metoffice.gov.uk/weather/warnings-and-advice/seasonal-advice/pollen-forecast"

POLLEN_FORECAST_REGEX = (
    r"window.metoffice.component.pollenForecast.pollenForecastList.*?(\[.*\]);"
)


class Region:
    """A region.
    e.g., the West Midlands is
    {
        "id": "wm",
        "name": "West Midlands"
    }
    """

    id: str
    name: str

    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Region):
            return NotImplemented
        return self.id == other.id and self.name == other.name

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"


class PollenLevel(Enum):
    """Pollen levels given by Met Office."""

    UNKNOWN = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4

    def __str__(self) -> str:
        return format_pollen_level(self)


def pollen_level_from_string(string: str) -> PollenLevel:
    """Get a pollen level from the short string sent by Met Office."""
    if string == "L":
        return PollenLevel.LOW
    if string == "M":
        return PollenLevel.MEDIUM
    if string == "H":
        return PollenLevel.HIGH
    if string == "VH":
        return PollenLevel.VERY_HIGH
    return PollenLevel.UNKNOWN


def format_pollen_level(pollen_level: PollenLevel) -> str:
    """Format a pollen level for display."""
    if pollen_level == PollenLevel.LOW:
        return "Low"
    if pollen_level == PollenLevel.MEDIUM:
        return "Medium"
    if pollen_level == PollenLevel.HIGH:
        return "High"
    if pollen_level == PollenLevel.VERY_HIGH:
        return "Very High"
    return "Unknown"


class DayForecast:
    """A forecast for a day."""

    date: datetime.date
    pollen_level: PollenLevel

    def __init__(self, date: datetime.date, pollen_level: PollenLevel):
        self.date = date
        self.pollen_level = pollen_level

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DayForecast):
            return NotImplemented
        return self.date == other.date and self.pollen_level == other.pollen_level

    def __str__(self) -> str:
        return f"{self.date}: {self.pollen_level}"


class Forecast:
    """A forecast for a region."""

    region: Region
    days: list[DayForecast]

    def __init__(self, region: Region, days: list[DayForecast]):
        self.region = region
        self.days = days

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Forecast):
            return NotImplemented
        return self.region == other.region and self.days == other.days

    def __str__(self) -> str:
        return f"{self.region}: {self.days}"


def get_forecast_for_region(
    forecasts: list[Forecast], region_id: str
) -> Forecast | None:
    """Get the forecast for a region.
    Args:
        forecasts (list): List of forecasts
        region_id (str): Region ID
    Returns:
        Forecast: Forecast for the region
        None: If region ID is not found in forecasts
    """
    return next(
        (
            reg_forecast
            for reg_forecast in forecasts
            if reg_forecast.region.id == region_id
        ),
        None,
    )


def get_forecasts(timeout=10) -> list[Forecast]:
    """Get pollen forecasts from Met Office website.

    Args:
        timeout (int, optional): Request timeout in seconds. Defaults to 10.

    Raises:
        LookupError: If forecast can't be found in response

    Returns:
        list[Forecast]: List of forecasts
    """
    response = requests.get(POLLEN_FORECAST_URL, timeout=timeout)
    if response.status_code != 200:
        response.raise_for_status()

    forecast_regex = re.search(POLLEN_FORECAST_REGEX, response.text)
    if forecast_regex is None:
        raise LookupError("Couldn't find forecast in response.")

    forecast_json = json.loads(forecast_regex.group(1))
    forecasts = []
    for forecast in forecast_json:
        region = Region(forecast["id"], forecast["regionName"])
        days = []
        for i, pollen_level in enumerate(forecast["pollenLevel"]):
            date = datetime.date.today() + datetime.timedelta(days=i)
            pollen_level = pollen_level_from_string(pollen_level)
            days.append(DayForecast(date, pollen_level))
        forecasts.append(Forecast(region, days))
    return forecasts


def get_regions(timeout=10) -> list[Region]:
    """Get regions from Met Office website.

    Args:
        timeout (int, optional): Request timeout in seconds. Defaults to 10.

    Returns:
        list[Region]: List of regions
    """
    forecasts = get_forecasts(timeout=timeout)
    regions = []
    for forecast in forecasts:
        regions.append(forecast.region)
    return regions


def _main():
    forecasts = get_forecasts()
    for forecast in forecasts:
        print(forecast.region)
        for day in forecast.days:
            print(day)


if __name__ == "__main__":
    _main()
