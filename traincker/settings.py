"""Paramètres utilisateur pour les alertes (canal, heures de silence, météo)."""

import json
from pathlib import Path

PARAMETRES_PATH = Path(__file__).resolve().parent.parent / "config" / "parametres.json"

DEFAUTS = {
    "silence_debut": "22:00",
    "silence_fin": "07:00",
    "canal_discord": True,
    "canal_email": False,
    "email_destinataire": "",
    "alertes_meteo": True,
    "contraste_eleve": False,
    "taille_police": "normale",
    "langue": "fr",
    "theme_clair": False,
}


def charger_parametres(path: Path = PARAMETRES_PATH) -> dict:
    if not path.exists():
        return DEFAUTS.copy()
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    parametres = DEFAUTS.copy()
    parametres.update(data)
    return parametres


def sauvegarder_parametres(parametres: dict, path: Path = PARAMETRES_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(parametres, f, ensure_ascii=False, indent=2)
