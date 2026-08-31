import requests
from langchain_core.tools import tool


# this dict maps the WMO weather codes to readable descriptions
# source: https://open-meteo.com/en/docs (WMO code table)
WEATHER_CODES = {
    0:  "Clear sky ☀️",
    1:  "Mainly clear 🌤️",
    2:  "Partly cloudy ⛅",
    3:  "Overcast ☁️",
    45: "Foggy 🌫️",
    48: "Icy fog 🌫️",
    51: "Light drizzle 🌦️",
    53: "Moderate drizzle 🌦️",
    55: "Heavy drizzle 🌧️",
    61: "Slight rain 🌧️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain 🌧️",
    71: "Slight snowfall 🌨️",
    73: "Moderate snowfall 🌨️",
    75: "Heavy snowfall ❄️",
    80: "Slight rain showers 🌦️",
    81: "Moderate rain showers 🌧️",
    82: "Heavy rain showers ⛈️",
    95: "Thunderstorm ⛈️",
    96: "Thunderstorm with hail ⛈️",
    99: "Thunderstorm with heavy hail ⛈️",
}


@tool
def get_weather_forecast(city: str) -> str:
    """
    Fetches tomorrow's weather forecast for a given city.
    Returns temperature, rain chance, rainfall amount, and weather condition.
    Call this tool whenever the user asks anything about weather, rain, umbrella,
    raincoat, getting wet, or outdoor conditions for tomorrow.
    """

    # --- step 1: find lat/lon of the city using geocoding ---
    print(f"\n[Tool] Looking up coordinates for: {city}")

    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo_resp = requests.get(geo_url, timeout=10)
    geo_data = geo_resp.json()

    # if city not found, tell the LLM
    if not geo_data.get("results"):
        return f"Could not find the city '{city}'. Please try a different city name."

    lat       = geo_data["results"][0]["latitude"]
    lon       = geo_data["results"][0]["longitude"]
    city_name = geo_data["results"][0]["name"]

    print(f"[Tool] Found: {city_name} at ({lat}, {lon})")

    # --- step 2: fetch the 2-day forecast (index 0 = today, index 1 = tomorrow) ---
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,"
        f"precipitation_probability_max,precipitation_sum,weathercode"
        f"&timezone=Asia%2FKolkata"
        f"&forecast_days=2"
    )

    weather_resp = requests.get(weather_url, timeout=10)
    weather_data = weather_resp.json()

    daily = weather_data["daily"]

    # index 1 = tomorrow's data
    max_temp   = daily["temperature_2m_max"][1]
    min_temp   = daily["temperature_2m_min"][1]
    rain_prob  = daily["precipitation_probability_max"][1]  # percentage
    rain_mm    = daily["precipitation_sum"][1]              # millimeters
    w_code     = daily["weathercode"][1]

    # convert code to a description
    condition = WEATHER_CODES.get(w_code, f"Unknown (code {w_code})")

    print(f"[Tool] Tomorrow's data fetched. Rain chance: {rain_prob}%")

    # build a clean string result for the LLM to read
    result = f"""
Tomorrow's weather forecast for {city_name}:
- Max Temperature  : {max_temp}°C
- Min Temperature  : {min_temp}°C
- Rain Probability : {rain_prob}%
- Expected Rainfall: {rain_mm} mm
- Condition        : {condition}
    """.strip()

    return result
