"""
Wrapper autour de l'API SNCF (basée sur Navitia).

Documentation officielle : https://doc.navitia.io/#getting-started

Authentification : Basic Auth avec la clé API en tant que username,
et un mot de passe vide.
"""

import os
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.sncf.com/v1/coverage/sncf"


class NavitiaAPIError(Exception):
    """Erreur levée quand l'API SNCF renvoie une erreur."""


class NavitiaClient:
    """Client simple pour interroger l'API SNCF (Navitia)."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SNCF_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Clé API SNCF manquante. Ajoute SNCF_API_KEY dans ton fichier .env"
            )
        self.session = requests.Session()
        self.session.auth = (self.api_key, "")

    def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Effectue une requête GET sur l'API et gère les erreurs de base."""
        url = f"{BASE_URL}{endpoint}"
        response = self.session.get(url, params=params or {})

        if response.status_code != 200:
            raise NavitiaAPIError(
                f"Erreur API ({response.status_code}) sur {url} : {response.text}"
            )
        return response.json()

    def search_station(self, query: str, count: int = 5) -> list[dict]:
        """
        Recherche une ou plusieurs gares à partir d'un nom (ex: "Dijon").

        Retourne une liste de dicts avec au minimum 'id' et 'name'.
        """
        data = self._get(
            "/places",
            params={"q": query, "type[]": "stop_area", "count": count},
        )
        places = data.get("places", [])
        return [
            {"id": place["id"], "name": place["name"]}
            for place in places
            if place.get("embedded_type") == "stop_area"
        ]

    def get_next_departures(self, stop_area_id: str, count: int = 10) -> list[dict]:
        """
        Récupère les prochains départs pour une gare donnée (stop_area).

        Retourne une liste de dicts simplifiés : ligne, direction, heure
        prévue, heure théorique, statut (à l'heure / retard / supprimé).
        """
        data = self._get(
            f"/stop_areas/{stop_area_id}/departures",
            params={"count": count},
        )

        departures = []
        for dep in data.get("departures", []):
            stop_dt = dep["stop_date_time"]
            info = dep["display_informations"]

            departures.append(
                {
                    "ligne": info.get("label") or info.get("code"),
                    "direction": info.get("direction"),
                    "heure_theorique": stop_dt.get("base_departure_date_time"),
                    "heure_prevue": stop_dt.get("departure_date_time"),
                    "statut": stop_dt.get("data_freshness", "base_schedule"),
                }
            )
        return departures

    def get_disruptions(self, stop_area_id: str) -> list[dict]:
        """Récupère les perturbations en cours affectant une gare donnée."""
        data = self._get(f"/stop_areas/{stop_area_id}/line_reports")
        disruptions = data.get("disruptions", [])
        return [
            {
                "titre": d.get("cause", "Perturbation"),
                "message": d.get("messages", [{}])[0].get("text", ""),
                "severite": d.get("severity", {}).get("effect"),
            }
            for d in disruptions
        ]
