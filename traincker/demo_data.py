"""
Client factice pour le mode démo : génère des données plausibles sans
appeler l'API SNCF ni exposer de vraie clé. Utile pour montrer le projet
(captures d'écran, portfolio) sans dépendre d'identifiants réels.
"""

import random
from datetime import datetime, timedelta

_GARES_DEMO = [
    {"id": "demo:1", "name": "Paris Gare de Lyon"},
    {"id": "demo:2", "name": "Lyon Part-Dieu"},
    {"id": "demo:3", "name": "Marseille Saint-Charles"},
    {"id": "demo:4", "name": "Bordeaux Saint-Jean"},
    {"id": "demo:5", "name": "Lille Flandres"},
    {"id": "demo:6", "name": "Strasbourg"},
    {"id": "demo:7", "name": "Nantes"},
    {"id": "demo:8", "name": "Toulouse Matabiau"},
]

_LIGNES_DEMO = ["TGV INOUI 6201", "TER 83512", "TGV INOUI 6842", "TER 91045", "OUIGO 7418"]

_DISRUPTION_TEMPLATES = [
    ("Travaux sur la voie", "Ralentissement ponctuel entre deux gares."),
    ("Incident technique", "Un incident matériel affecte la circulation."),
    ("Affluence exceptionnelle", "Trafic dense, léger retard possible."),
]


class DemoNavitiaClient:
    """Simule NavitiaClient avec des données fictives cohérentes."""

    def search_station(self, query: str, count: int = 5) -> list[dict]:
        query_lower = query.lower()
        resultats = [g for g in _GARES_DEMO if query_lower in g["name"].lower()]
        return resultats[:count] if resultats else _GARES_DEMO[:count]

    def get_next_departures(self, stop_area_id: str, count: int = 10) -> list[dict]:
        maintenant = datetime.now()
        departs = []
        for i in range(count):
            heure_theorique = maintenant + timedelta(minutes=8 * (i + 1))
            en_retard = random.random() < 0.25
            heure_prevue = heure_theorique + (
                timedelta(minutes=random.randint(3, 18)) if en_retard else timedelta()
            )
            departs.append(
                {
                    "ligne": random.choice(_LIGNES_DEMO),
                    "direction": random.choice(_GARES_DEMO)["name"],
                    "heure_theorique": heure_theorique.strftime("%Y%m%dT%H%M%S"),
                    "heure_prevue": heure_prevue.strftime("%Y%m%dT%H%M%S"),
                    "statut": "realtime" if en_retard else "base_schedule",
                }
            )
        return departs

    def get_disruptions(self, stop_area_id: str) -> list[dict]:
        if random.random() < 0.3:
            titre, message = random.choice(_DISRUPTION_TEMPLATES)
            return [{"titre": titre, "message": message, "severite": "delayed"}]
        return []


def obtenir_favoris_demo():
    """Trajets favoris fictifs pour illustrer l'onglet Favoris en mode démo."""
    from traincker.models import Trajet

    return [
        Trajet(
            nom="Domicile -> Travail",
            gare_depart_id="demo:1",
            gare_depart_nom="Paris Gare de Lyon",
            gare_arrivee_id="demo:2",
            gare_arrivee_nom="Lyon Part-Dieu",
            actif=True,
        ),
        Trajet(
            nom="Week-end famille",
            gare_depart_id="demo:2",
            gare_depart_nom="Lyon Part-Dieu",
            gare_arrivee_id="demo:3",
            gare_arrivee_nom="Marseille Saint-Charles",
            actif=True,
        ),
    ]
