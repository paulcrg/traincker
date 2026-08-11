"""Envoi d'alertes via webhook Discord et/ou email."""

import os
import smtplib
from email.mime.text import MIMEText
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()


class AlertError(Exception):
    pass


GRAVITE_LABELS = {
    "NO_SERVICE": ("Critique", "Rouge"),
    "REDUCED_SERVICE": ("Important", "Orange"),
    "SIGNIFICANT_DELAYS": ("Important", "Orange"),
    "DETOUR": ("Modéré", "Jaune"),
    "MODIFIED_SERVICE": ("Modéré", "Jaune"),
    "STOP_MOVED": ("Modéré", "Jaune"),
    "ADDITIONAL_SERVICE": ("Info", "Bleu"),
    "OTHER_EFFECT": ("Mineur", "Jaune"),
    "UNKNOWN_EFFECT": ("Mineur", "Jaune"),
}


def gravite_perturbation(severite: Optional[str]) -> tuple[str, str]:
    return GRAVITE_LABELS.get(severite, ("Mineur", "Jaune"))


def est_critique(severite: Optional[str]) -> bool:
    return severite == "NO_SERVICE"


def send_discord_alert(message: str, webhook_url: Optional[str] = None) -> None:
    url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
    if not url:
        raise ValueError("URL de webhook Discord manquante. Ajoute DISCORD_WEBHOOK_URL dans .env")

    response = requests.post(url, json={"content": message}, timeout=8)
    if response.status_code != 204:
        raise AlertError(f"Échec de l'envoi Discord ({response.status_code}) : {response.text}")


def send_email_alert(subject: str, message: str, destinataire: str) -> None:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")

    if not all([host, user, password, destinataire]):
        raise ValueError("Configuration email incomplète (SMTP_HOST/USER/PASSWORD, destinataire).")

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = destinataire

    with smtplib.SMTP(host, port, timeout=10) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)


def format_perturbation_message(trajet_nom: str, perturbations: list[dict]) -> str:
    lignes = [f"Perturbation sur ton trajet « {trajet_nom} »"]
    for p in perturbations:
        label, _ = gravite_perturbation(p.get("severite"))
        lignes.append(f"[{label}] {p['titre']} : {p['message']}")
    return "\n".join(lignes)
