"""
Historisation des départs collectés via l'API SNCF.

Écrit dans Supabase si configuré (SUPABASE_URL/SUPABASE_KEY présents) —
nécessaire pour que le dashboard hébergé sur Render voie les données
collectées par le cron GitHub Actions sans redéploiement. Sinon, retombe
sur un CSV local (dev local).

Sur Supabase, l'horodatage est stocké en UTC (bonne pratique serveur) ;
en local, en heure de la machine (comportement historique, déjà correct
pour un usage mono-poste).
"""

import csv
from datetime import datetime
from pathlib import Path

from traincker.db import inserer_departs, est_configure
from traincker.tz_utils import maintenant_utc

CSV_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "processed" / "departures.csv"
)

COLONNES = [
    "horodatage_collecte", "gare", "ligne", "direction",
    "heure_theorique", "heure_prevue", "statut",
]


def historiser_departs(departs: list[dict], gare_nom: str, path: Path = CSV_PATH) -> None:
    """Historise une liste de départs, dans Supabase si configuré, sinon en CSV local."""
    if est_configure():
        inserer_departs(departs, gare_nom, maintenant_utc().isoformat())
        return

    horodatage = datetime.now().isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    fichier_existe = path.exists()

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLONNES)
        if not fichier_existe:
            writer.writeheader()

        for d in departs:
            writer.writerow({
                "horodatage_collecte": horodatage,
                "gare": gare_nom,
                "ligne": d["ligne"],
                "direction": d["direction"],
                "heure_theorique": d["heure_theorique"],
                "heure_prevue": d["heure_prevue"],
                "statut": d["statut"],
            })
