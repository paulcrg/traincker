"""Cache disque simple pour les recherches de gares et le mode dégradé."""

import json
import time
from pathlib import Path
from typing import Any, Optional

CACHE_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "cache_local.json"
DUREE_VALIDITE_DEFAUT = 60 * 60 * 24


def _charger_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    try:
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _sauvegarder_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def obtenir(cle: str, duree_validite: int = DUREE_VALIDITE_DEFAUT) -> Optional[Any]:
    entree = _charger_cache().get(cle)
    if not entree:
        return None
    if time.time() - entree["horodatage"] > duree_validite:
        return None
    return entree["valeur"]


def obtenir_meme_expire(cle: str) -> Optional[tuple]:
    entree = _charger_cache().get(cle)
    if not entree:
        return None
    return entree["valeur"], entree["horodatage"]


def enregistrer(cle: str, valeur: Any) -> None:
    cache = _charger_cache()
    cache[cle] = {"valeur": valeur, "horodatage": time.time()}
    _sauvegarder_cache(cache)
