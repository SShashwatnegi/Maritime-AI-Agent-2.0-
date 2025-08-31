import requests
from datetime import datetime, timedelta
from app.config import settings
from geopy.geocoders import Nominatim

class WeatherService:
    def __init__(self):
        self.api_key = settings.OPENWEATHERMAP_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5/forecast"
        self.geolocator = Nominatim(user_agent="maritime_agent")

    def resolve_location(self, location: str):
        try:
            lat_str, lon_str = location.split(",")
            return float(lat_str.strip()), float(lon_str.strip())
        except ValueError:
            loc = self.geolocator.geocode(location)
            if not loc:
                raise ValueError(f"Could not resolve location: {location}")
            return loc.latitude, loc.longitude

    def get_weather_forecast(self, lat: float, lon: float, hours: int = 48):
        url = f"{self.base_url}?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        forecast = []
        now = datetime.utcnow()
        cutoff = now + timedelta(hours=hours)

        for item in data["list"]:
            dt = datetime.utcfromtimestamp(item["dt"])
            if dt > cutoff:
                break
            forecast.append({
                "time": dt.isoformat(),  # always string
                "temperature": item["main"]["temp"],
                "condition": item["weather"][0]["description"]
            })
        return forecast

    def get_bad_weather_periods(self, lat: float, lon: float, hours: int = 48):
        forecast = self.get_weather_forecast(lat, lon, hours)
        bad_periods = []
        current_bad = None

        for entry in forecast:
            condition = entry["condition"].lower()
            dt = datetime.fromisoformat(entry["time"])
            if any(w in condition for w in ["rain", "storm", "fog", "snow"]):
                if current_bad is None:
                    current_bad = dt
            else:
                if current_bad is not None:
                    bad_periods.append((current_bad.isoformat(), dt.isoformat()))
                    current_bad = None

        if current_bad is not None:
            bad_periods.append((current_bad.isoformat(), datetime.fromisoformat(forecast[-1]["time"]).isoformat()))

        return bad_periods

    def forecast_by_location(self, location: str, hours: int = 48):
        lat, lon = self.resolve_location(location)
        return self.get_weather_forecast(lat, lon, hours)

    def bad_periods_by_location(self, location: str, hours: int = 48):
        lat, lon = self.resolve_location(location)
        return self.get_bad_weather_periods(lat, lon, hours)
