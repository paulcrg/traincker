"""Vérification météo légère via Open-Meteo (gratuit, sans clé API)."""

import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

CODES_DEFAVORABLES = {
    71: "Neige faible", 73: "Neige modérée", 75: "Neige forte", 77: "Grains de neige",
    85: "Averses de neige", 86: "Averses de neige fortes",
    65: "Pluie forte", 82: "Averses violentes",
    95: "Orage", 96: "Orage avec grêle", 99: "Orage violent avec grêle",
}

TIMEOUT_SECONDES = 6


def verifier_meteo_defavorable(nom_gare: str) -> dict | None:
    try:
        geo = requests.get(
            GEOCODING_URL,
            params={"name": nom_gare, "count": 1, "language": "fr"},
            timeout=TIMEOUT_SECONDES,
        ).json()
        resultats = geo.get("results")
        if not resultats:
            return None

        lat, lon = resultats[0]["latitude"], resultats[0]["longitude"]

        meteo = requests.get(
            FORECAST_URL,
            params={"latitude": lat, "longitude": lon, "current": "weather_code,temperature_2m"},
            timeout=TIMEOUT_SECONDES,
        ).json()
        code = meteo.get("current", {}).get("weather_code")

        if code in CODES_DEFAVORABLES:
            return {
                "condition": CODES_DEFAVORABLES[code],
                "temperature": meteo["current"].get("temperature_2m"),
            }
        return None
    except (requests.exceptions.RequestException, KeyError, ValueError, TypeError):
        return None
