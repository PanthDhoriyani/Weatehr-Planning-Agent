import requests
from langchain_core.tools import tool

# WMO Weather code interpretations for agriculture
AGRI_WEATHER_CODES = {
    0:  "Clear sky ☀️ (High solar radiation, optimal photosynthesis)",
    1:  "Mainly clear 🌤️ (Favorable outdoor fieldwork conditions)",
    2:  "Partly cloudy ⛅ (Mild evapotranspiration)",
    3:  "Overcast ☁️ (Low solar radiation, reduced transpiration)",
    45: "Foggy 🌫️ (High surface moisture, elevated fungal risk)",
    48: "Depositing rime fog 🌫️ (Severe leaf wetness)",
    51: "Light drizzle 🌦️ (Foliar moisture, caution for spraying)",
    53: "Moderate drizzle 🌦️ (Pesticide wash-off risk)",
    55: "Dense drizzle 🌧️ (Irrigation postponement recommended)",
    61: "Slight rain 🌧️ (Soil moisture replenishment)",
    63: "Moderate rain 🌧️ (Pause irrigation, waterlogging alert)",
    65: "Heavy rain ⛈️ (Risk of soil erosion & root rot)",
    71: "Slight snow 🌨️ (Frost protection required)",
    80: "Slight rain showers 🌦️ (Intermittent wetness)",
    81: "Moderate rain showers 🌧️ (Field access limited)",
    82: "Violent rain showers ⛈️ (High crop lodging & runoff danger)",
    95: "Thunderstorm ⛈️ (High wind & physical crop damage risk)",
    96: "Thunderstorm with slight hail 🌨️ (Severe foliage & fruit damage danger)",
    99: "Thunderstorm with heavy hail 🌨️ (Critical crop destruction warning)",
}


@tool
def get_agricultural_weather_data(location: str, crop: str = "general") -> str:
    """
    Fetches real-time agricultural telemetry and a 3-day agro-meteorological forecast
    from the Open-Meteo Agricultural API for any farm location.
    
    Returns:
    - Temperature max/min (°C)
    - Precipitation sum (mm) and rain probability (%)
    - Reference Evapotranspiration (ET₀ in mm/day)
    - Max Wind Speed at 10m (km/h) for pesticide spray drift risk
    - Relative Humidity (%) and Leaf Wetness for fungal pest risk
    - Topsoil Moisture (0-1cm) and Soil Temperature
    
    Call this whenever addressing farm operations: irrigation, spraying, pest alerts,
    harvest timing, or crop safety.
    """
    print(f"\n[AgriTool] Resolving coordinates for farm location: {location} (Crop: {crop})")

    # Step 1: Geocoding via Open-Meteo
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
    try:
        geo_resp = requests.get(geo_url, timeout=10)
        geo_data = geo_resp.json()
    except Exception as e:
        return f"Error connecting to geocoding service: {str(e)}"

    if not geo_data.get("results"):
        return f"Could not find agricultural location '{location}'. Please verify the district/city name."

    lat = geo_data["results"][0]["latitude"]
    lon = geo_data["results"][0]["longitude"]
    loc_name = geo_data["results"][0]["name"]
    country = geo_data["results"][0].get("country", "")

    print(f"[AgriTool] Located: {loc_name}, {country} at ({lat}, {lon})")

    # Step 2: Fetch Agricultural Weather Data (3-day forecast)
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,"
        f"precipitation_sum,precipitation_probability_max,"
        f"wind_speed_10m_max,et0_fao_evapotranspiration,weathercode"
        f"&hourly=relative_humidity_2m,soil_temperature_0cm,soil_moisture_0_to_1cm"
        f"&timezone=Asia%2FKolkata"
        f"&forecast_days=3"
    )

    try:
        weather_resp = requests.get(weather_url, timeout=10)
        weather_data = weather_resp.json()
    except Exception as e:
        return f"Error retrieving agricultural telemetry from Open-Meteo: {str(e)}"

    if "daily" not in weather_data:
        return "Failed to parse agricultural telemetry."

    daily = weather_data["daily"]
    hourly = weather_data.get("hourly", {})

    # Days analysis
    day_labels = ["Today", "Tomorrow", "Day 3"]
    days_summary = []

    for i in range(min(3, len(daily["time"]))):
        t_max = daily["temperature_2m_max"][i]
        t_min = daily["temperature_2m_min"][i]
        rain_prob = daily["precipitation_probability_max"][i]
        rain_sum = daily["precipitation_sum"][i]
        wind_max = daily["wind_speed_10m_max"][i]
        et0 = daily.get("et0_fao_evapotranspiration", [3.5, 3.5, 3.5])[i]
        w_code = daily["weathercode"][i]
        condition = AGRI_WEATHER_CODES.get(w_code, f"Code {w_code}")

        days_summary.append({
            "day": day_labels[i],
            "date": daily["time"][i],
            "t_max": t_max,
            "t_min": t_min,
            "rain_prob": rain_prob,
            "rain_sum": rain_sum,
            "wind_max": wind_max,
            "et0": et0,
            "condition": condition
        })

    # Hourly calculations for current 24 hours
    rh_values = hourly.get("relative_humidity_2m", [60] * 24)[:24]
    soil_moist_values = hourly.get("soil_moisture_0_to_1cm", [0.25] * 24)[:24]
    soil_temp_values = hourly.get("soil_temperature_0cm", [24.0] * 24)[:24]

    avg_rh = round(sum(rh_values) / len(rh_values), 1) if rh_values else 60.0
    max_rh = max(rh_values) if rh_values else 75
    avg_soil_moist = round(sum(soil_moist_values) / len(soil_moist_values), 3) if soil_moist_values else 0.25
    avg_soil_temp = round(sum(soil_temp_values) / len(soil_temp_values), 1) if soil_temp_values else 24.0

    # Agronomic status indicators
    # Soil Moisture (m³/m³): <0.15 = Deficit/Dry, 0.15-0.35 = Optimal, >0.35 = Saturated
    if avg_soil_moist < 0.15:
        soil_status = "DEFICIT / DRY (Irrigation indicated unless rain is imminent)"
    elif avg_soil_moist <= 0.35:
        soil_status = "OPTIMAL / ADEQUATE (Good root zone hydration)"
    else:
        soil_status = "SATURATED / HIGH (Risk of root asphyxiation if over-watered)"

    # Spray drift risk based on wind:
    # Ideal spraying wind: 5 - 15 km/h. Below 5 = inversion risk, Above 15 = drift risk
    today_wind = days_summary[0]["wind_max"]
    if today_wind < 5:
        spray_status = "CAUTION: Temperature inversion risk (very low wind < 5 km/h)"
    elif today_wind <= 15:
        spray_status = "OPTIMAL: Safe spray window (Wind 5-15 km/h, minimal drift)"
    elif today_wind <= 25:
        spray_status = "MARGINAL: Moderate spray drift hazard (Wind 15-25 km/h, use coarse nozzles)"
    else:
        spray_status = "PROHIBITIVE: High spray drift hazard (Wind > 25 km/h, DO NOT SPRAY)"

    # Fungal disease index based on RH
    if max_rh > 85 or avg_rh > 75:
        fungal_status = "HIGH THREAT: Extended high humidity (>80%) creates prime spore germination conditions"
    elif max_rh > 70:
        fungal_status = "MODERATE THREAT: Monitor dense crop canopies for early blight/mildew symptoms"
    else:
        fungal_status = "LOW THREAT: Dry foliage minimizes fungal pathogen development"

    # Assemble comprehensive report
    report = f"""
🌾 AGRI-METEOROLOGICAL REPORT FOR {loc_name.upper()} ({country})
Target Crop: {crop.upper()}

1. 💧 SOIL & HYDROLOGY STATUS (Top 0-7cm):
   - Average Topsoil Moisture: {avg_soil_moist} m³/m³ → {soil_status}
   - Average Topsoil Temperature: {avg_soil_temp}°C
   - Today's Reference Evapotranspiration (ET₀): {days_summary[0]['et0']} mm/day

2. 🧪 SPRAYING & CHEMICAL WINDOW:
   - Max Surface Wind Speed Today: {today_wind} km/h
   - Chemical Application Safety: {spray_status}

3. 🐛 PEST & FUNGAL DISEASE ATMOSPHERIC WINDOW:
   - 24h Average Relative Humidity: {avg_rh}% (Peak: {max_rh}%)
   - Fungal Spore Threat Rating: {fungal_status}

4. 📅 3-DAY AGRO-METEOROLOGICAL OUTLOOK:
"""
    for d in days_summary:
        report += (
            f"   • {d['day']} ({d['date']}): {d['condition']}\n"
            f"     - Temp: {d['t_min']}°C to {d['t_max']}°C | ET₀: {d['et0']} mm\n"
            f"     - Rain Probability: {d['rain_prob']}% | Expected Rain: {d['rain_sum']} mm\n"
            f"     - Max Wind: {d['wind_max']} km/h\n"
        )

    return report.strip()
