"""
Historisation des départs collectés via l'API SNCF dans un CSV.

Chaque appel à historiser_departs() ajoute une ligne par départ récupéré,
avec un horodatage de collecte. Ce CSV alimente ensuite traincker/analysis.py.
"""

import csv
from datetime import datetime
from pathlib import Path

CSV_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "processed" / "departures.csv"
)

COLONNES = [
    "horodatage_collecte",
    "gare",
    "ligne",
    "direction",
    "heure_theorique",
    "heure_prevue",
    "statut",
]


def historiser_departs(departs: list[dict], gare_nom: str, path: Path = CSV_PATH) -> None:
    """
    Ajoute les départs récupérés au CSV d'historique (une ligne par départ).

    Crée le fichier et l'en-tête s'ils n'existent pas encore.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fichier_existe = path.exists()

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLONNES)
        if not fichier_existe:
            writer.writeheader()

        horodatage = datetime.now().isoformat()
        for d in departs:
            writer.writerow(
                {
                    "horodatage_collecte": horodatage,
                    "gare": gare_nom,
                    "ligne": d["ligne"],
                    "direction": d["direction"],
                    "heure_theorique": d["heure_theorique"],
                    "heure_prevue": d["heure_prevue"],
                    "statut": d["statut"],
                }
            )
