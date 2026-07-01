"""
Envoi d'alertes via un webhook Discord.

Pour obtenir une URL de webhook :
Discord > Paramètres du salon > Intégrations > Webhooks > Nouveau webhook
"""

import os
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()


class AlertError(Exception):
    """Erreur levée quand l'envoi d'une alerte échoue."""


def send_discord_alert(message: str, webhook_url: Optional[str] = None) -> None:
    """
    Envoie un message texte simple sur un salon Discord via webhook.

    Lève AlertError si l'envoi échoue.
    """
    url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
    if not url:
        raise ValueError(
            "URL de webhook Discord manquante. Ajoute DISCORD_WEBHOOK_URL dans .env"
        )

    response = requests.post(url, json={"content": message})

    # Discord renvoie 204 No Content en cas de succès
    if response.status_code != 204:
        raise AlertError(
            f"Échec de l'envoi Discord ({response.status_code}) : {response.text}"
        )


def format_perturbation_message(trajet_nom: str, perturbations: list[dict]) -> str:
    """Construit un message Discord lisible à partir d'une liste de perturbations."""
    lignes = [f"🚨 **Perturbation sur ton trajet « {trajet_nom} »**"]
    for p in perturbations:
        lignes.append(f"- {p['titre']} : {p['message']}")
    return "\n".join(lignes)
