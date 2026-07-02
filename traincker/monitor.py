"""
Boucle de surveillance des trajets favoris.

Vérifie périodiquement les perturbations sur chaque trajet actif et
envoie une alerte Discord uniquement pour les perturbations nouvelles
(évite de spammer le même message à chaque vérification).
"""

import hashlib
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

import schedule

from traincker.api_client import NavitiaClient, NavitiaAPIError
from traincker.alerts import send_discord_alert, format_perturbation_message
from traincker.favoris import charger_favoris

ETAT_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
    / "alertes_envoyees.json"
)

# Ne pas ré-alerter sur la même perturbation avant ce délai
DELAI_RE_ALERTE = timedelta(hours=6)


def _hash_perturbation(p: dict) -> str:
    """Identifiant stable d'une perturbation, pour détecter les doublons."""
    contenu = f"{p['titre']}|{p['message']}"
    return hashlib.md5(contenu.encode("utf-8")).hexdigest()


def _charger_etat() -> dict:
    if not ETAT_PATH.exists():
        return {}
    with open(ETAT_PATH, encoding="utf-8") as f:
        return json.load(f)


def _sauvegarder_etat(etat: dict) -> None:
    ETAT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ETAT_PATH, "w", encoding="utf-8") as f:
        json.dump(etat, f, ensure_ascii=False, indent=2)


def verifier_favoris(client: NavitiaClient = None) -> None:
    """
    Vérifie tous les trajets favoris actifs et envoie une alerte Discord
    pour toute perturbation qui n'a pas déjà été signalée récemment.
    """
    client = client or NavitiaClient()
    etat = _charger_etat()
    maintenant = datetime.now()

    trajets = [t for t in charger_favoris() if t.actif]
    if not trajets:
        print(f"[{maintenant:%H:%M:%S}] Aucun trajet favori actif à vérifier.")
        return

    for trajet in trajets:
        try:
            perturbations = client.get_disruptions(trajet.gare_depart_id)
            perturbations += client.get_disruptions(trajet.gare_arrivee_id)
        except NavitiaAPIError as e:
            print(f"[{maintenant:%H:%M:%S}] Erreur API pour {trajet.nom} : {e}")
            continue

        nouvelles = []
        for p in perturbations:
            cle = _hash_perturbation(p)
            derniere_alerte = etat.get(cle)
            deja_recente = derniere_alerte and (
                maintenant - datetime.fromisoformat(derniere_alerte) < DELAI_RE_ALERTE
            )
            if not deja_recente:
                nouvelles.append(p)
                etat[cle] = maintenant.isoformat()

        if nouvelles:
            message = format_perturbation_message(trajet.nom, nouvelles)
            send_discord_alert(message)
            print(
                f"[{maintenant:%H:%M:%S}] Alerte envoyée pour {trajet.nom} "
                f"({len(nouvelles)} perturbation(s))"
            )
        else:
            print(f"[{maintenant:%H:%M:%S}] {trajet.nom} : RAS")

    _sauvegarder_etat(etat)


def lancer_surveillance(intervalle_minutes: int = 5) -> None:
    """Lance la boucle de surveillance en continu (bloquant, Ctrl+C pour arrêter)."""
    print(
        f"Surveillance démarrée (vérification toutes les {intervalle_minutes} min). "
        "Ctrl+C pour arrêter."
    )
    verifier_favoris()  # première vérification immédiate
    schedule.every(intervalle_minutes).minutes.do(verifier_favoris)

    while True:
        schedule.run_pending()
        time.sleep(1)
