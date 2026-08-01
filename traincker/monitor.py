"""
Boucle de surveillance des trajets favoris.

Vérifie périodiquement les perturbations sur chaque trajet actif et
envoie une alerte (Discord et/ou email) uniquement pour les perturbations
nouvelles. Respecte les heures de silence configurées (sauf perturbations
critiques) et peut alerter en cas de météo dégradée.
"""

import hashlib
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

import schedule

from traincker.api_client import NavitiaClient, NavitiaAPIError
from traincker.alerts import (
    send_discord_alert,
    send_email_alert,
    format_perturbation_message,
    est_critique,
)
from traincker.collector import historiser_departs
from traincker.favoris import charger_favoris
from traincker.settings import charger_parametres
from traincker.weather import verifier_meteo_defavorable
from traincker.reports import envoyer_rapport_hebdomadaire

ETAT_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
    / "alertes_envoyees.json"
)

# Ne pas ré-alerter sur la même perturbation (ou la même alerte météo) avant ce délai
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


def dans_le_silence(parametres: dict, maintenant: datetime) -> bool:
    """
    Détermine si l'heure actuelle tombe dans la plage de silence configurée.
    Gère le cas d'une plage qui traverse minuit (ex: 22:00 -> 07:00).
    """
    debut = parametres.get("silence_debut", "22:00")
    fin = parametres.get("silence_fin", "07:00")
    heure_actuelle = maintenant.strftime("%H:%M")

    if debut <= fin:
        return debut <= heure_actuelle < fin
    return heure_actuelle >= debut or heure_actuelle < fin


def _envoyer_alerte(message: str, sujet: str, parametres: dict) -> None:
    """Envoie sur les canaux activés dans les paramètres (Discord, email)."""
    if parametres.get("canal_discord", True):
        send_discord_alert(message)

    if parametres.get("canal_email") and parametres.get("email_destinataire"):
        try:
            send_email_alert(sujet, message, parametres["email_destinataire"])
        except (ValueError, OSError) as e:
            print(f"Erreur envoi email : {e}")


def verifier_favoris(client: NavitiaClient = None) -> None:
    """
    Vérifie tous les trajets favoris actifs et envoie une alerte pour toute
    perturbation nouvelle, en respectant les heures de silence, plus une
    alerte météo si des conditions dégradées sont détectées.
    """
    client = client or NavitiaClient()
    etat = _charger_etat()
    parametres = charger_parametres()
    maintenant = datetime.now()
    silence_actif = dans_le_silence(parametres, maintenant)

    trajets = [t for t in charger_favoris() if t.actif]
    if not trajets:
        print(f"[{maintenant:%H:%M:%S}] Aucun trajet favori actif à vérifier.")
        return

    for trajet in trajets:
        try:
            perturbations = client.get_disruptions(trajet.gare_depart_id)
            perturbations += client.get_disruptions(trajet.gare_arrivee_id)

            departs_depart = client.get_next_departures(trajet.gare_depart_id, count=10)
            historiser_departs(departs_depart, trajet.gare_depart_nom)

            departs_arrivee = client.get_next_departures(trajet.gare_arrivee_id, count=10)
            historiser_departs(departs_arrivee, trajet.gare_arrivee_nom)

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
            if silence_actif:
                a_envoyer = [p for p in nouvelles if est_critique(p.get("severite"))]
            else:
                a_envoyer = nouvelles

            if a_envoyer:
                message = format_perturbation_message(trajet.nom, a_envoyer)
                _envoyer_alerte(message, f"Traincker - {trajet.nom}", parametres)
                print(
                    f"[{maintenant:%H:%M:%S}] Alerte envoyée pour {trajet.nom} "
                    f"({len(a_envoyer)} perturbation(s))"
                )
            else:
                print(
                    f"[{maintenant:%H:%M:%S}] {trajet.nom} : perturbation mineure "
                    "ignorée (heures de silence)"
                )
        else:
            print(f"[{maintenant:%H:%M:%S}] {trajet.nom} : RAS")

        if parametres.get("alertes_meteo", True):
            meteo = verifier_meteo_defavorable(trajet.gare_depart_nom)
            if meteo:
                cle_meteo = f"meteo:{trajet.gare_depart_id}:{meteo['condition']}"
                derniere = etat.get(cle_meteo)
                deja_recente = derniere and (
                    maintenant - datetime.fromisoformat(derniere) < DELAI_RE_ALERTE
                )
                if not deja_recente:
                    msg_meteo = (
                        f"**Alerte météo pour « {trajet.nom} »**\n"
                        f"{meteo['condition']} à {trajet.gare_depart_nom} "
                        f"({meteo['temperature']}°C) — le trafic pourrait être affecté."
                    )
                    _envoyer_alerte(msg_meteo, f"Traincker - météo {trajet.nom}", parametres)
                    etat[cle_meteo] = maintenant.isoformat()

    _sauvegarder_etat(etat)


def lancer_surveillance(intervalle_minutes: int = 5) -> None:
    """Lance la boucle de surveillance en continu (bloquant, Ctrl+C pour arrêter)."""
    print(
        f"Surveillance démarrée (vérification toutes les {intervalle_minutes} min). "
        "Ctrl+C pour arrêter."
    )
    verifier_favoris()
    schedule.every(intervalle_minutes).minutes.do(verifier_favoris)
    schedule.every().monday.at("08:00").do(envoyer_rapport_hebdomadaire)

    while True:
        schedule.run_pending()
        time.sleep(1)
