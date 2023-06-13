"""Methods to grab pollen forecasts from the Met Office website.
Currently, the API doesn't support this, so we do some cheeky scraping.
"""
import re
import json
import requests

POLLEN_FORECAST_URL = "https://www.metoffice.gov.uk/weather/warnings-and-advice/seasonal-advice/pollen-forecast"

POLLEN_FORECAST_REGEX = (
    r"window.metoffice.component.pollenForecast.pollenForecastList.*?(\[.*\]);"
)


def get_forecast(timeout=10):
    """Get the pollen forecast from the Met Office website.
    Returns:
        list: A list of dicts containing the forecast for each region.
            keys:
                "id": string
                "regionName": string
                "pollenLevel": string[] (choice of "L", "M", "H", "VH")
    """
    response = requests.get(POLLEN_FORECAST_URL, timeout=timeout)
    if response.status_code != 200:
        response.raise_for_status()

    forecast = re.search(POLLEN_FORECAST_REGEX, response.text)
    if forecast is None:
        raise LookupError("Couldn't find forecast in response.")

    forecast = json.loads(forecast.group(1))
    return forecast


def _main():
    """test get_forecast"""
    forecast = get_forecast()
    print("forecast:\n", forecast)


if __name__ == "__main__":
    _main()
