"""
Envoi d'alertes via webhook Discord et/ou email.

Discord : Paramètres du salon > Intégrations > Webhooks > Nouveau webhook
Email : nécessite SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD dans .env
"""

import os
import smtplib
from email.mime.text import MIMEText
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()


class AlertError(Exception):
    """Erreur levée quand l'envoi d'une alerte échoue."""


# Correspondance entre les codes de gravité Navitia et un label/icône lisible
GRAVITE_LABELS = {
    "NO_SERVICE": ("Critique", "🔴"),
    "REDUCED_SERVICE": ("Important", "🟠"),
    "SIGNIFICANT_DELAYS": ("Important", "🟠"),
    "DETOUR": ("Modéré", "🟡"),
    "MODIFIED_SERVICE": ("Modéré", "🟡"),
    "STOP_MOVED": ("Modéré", "🟡"),
    "ADDITIONAL_SERVICE": ("Info", "🔵"),
    "OTHER_EFFECT": ("Mineur", "🟡"),
    "UNKNOWN_EFFECT": ("Mineur", "🟡"),
}


def gravite_perturbation(severite: Optional[str]) -> tuple[str, str]:
    """Retourne (label, icône) pour une perturbation, à partir de son code Navitia."""
    return GRAVITE_LABELS.get(severite, ("Mineur", "🟡"))


def est_critique(severite: Optional[str]) -> bool:
    """Une perturbation critique (suppression de service) ignore les heures de silence."""
    return severite == "NO_SERVICE"


def send_discord_alert(message: str, webhook_url: Optional[str] = None) -> None:
    """Envoie un message texte simple sur un salon Discord via webhook."""
    url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
    if not url:
        raise ValueError(
            "URL de webhook Discord manquante. Ajoute DISCORD_WEBHOOK_URL dans .env"
        )

    response = requests.post(url, json={"content": message}, timeout=8)

    if response.status_code != 204:
        raise AlertError(
            f"Échec de l'envoi Discord ({response.status_code}) : {response.text}"
        )


def send_email_alert(subject: str, message: str, destinataire: str) -> None:
    """Envoie une alerte par email via SMTP (identifiants dans .env)."""
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")

    if not all([host, user, password, destinataire]):
        raise ValueError(
            "Configuration email incomplète. Vérifie SMTP_HOST, SMTP_USER, "
            "SMTP_PASSWORD dans .env et l'adresse destinataire."
        )

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = destinataire

    with smtplib.SMTP(host, port, timeout=10) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)


def format_perturbation_message(trajet_nom: str, perturbations: list[dict]) -> str:
    """Construit un message lisible à partir d'une liste de perturbations, avec gravité."""
    lignes = [f"**Perturbation sur ton trajet « {trajet_nom} »**"]
    for p in perturbations:
        label, icone = gravite_perturbation(p.get("severite"))
        lignes.append(f"{icone} [{label}] {p['titre']} : {p['message']}")
    return "\n".join(lignes)
