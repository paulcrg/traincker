"""Chargement et sauvegarde des trajets favoris (config/favoris.json)."""

import json
from pathlib import Path

from traincker.models import Trajet

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "favoris.json"


def charger_favoris(path: Path = CONFIG_PATH) -> list[Trajet]:
    """Charge la liste des trajets favoris depuis le fichier JSON."""
    if not path.exists():
        return []

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    return [Trajet(**t) for t in data.get("trajets", [])]


def sauvegarder_favoris(trajets: list[Trajet], path: Path = CONFIG_PATH) -> None:
    """Sauvegarde la liste des trajets favoris dans le fichier JSON."""
    data = {
        "trajets": [
            {
                "nom": t.nom,
                "gare_depart_id": t.gare_depart_id,
                "gare_depart_nom": t.gare_depart_nom,
                "gare_arrivee_id": t.gare_arrivee_id,
                "gare_arrivee_nom": t.gare_arrivee_nom,
                "actif": t.actif,
            }
            for t in trajets
        ]
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
