"""
Connexion optionnelle à Supabase (PostgreSQL gratuit et permanent).

Sert de source de vérité partagée entre la surveillance GitHub Actions
(qui écrit) et le dashboard hébergé sur Render (qui lit) — Render ne se
redéploie pas à chaque commit, donc les fichiers locaux écrits par le
cron GitHub Actions ne seraient jamais vus par l'app en ligne sans ça.

Si SUPABASE_URL / SUPABASE_KEY ne sont pas configurés (ex: en local sans
compte Supabase), toutes les fonctions retournent None/False silencieusement
et le reste du code retombe sur les fichiers locaux (CSV/JSON).
"""

import os
from datetime import timedelta
from typing import Optional

from dotenv import load_dotenv

from traincker.tz_utils import maintenant_utc, parser_utc_tolerant

load_dotenv()

_client = None
_tentative_faite = False


def obtenir_client():
    """Retourne le client Supabase configuré, ou None si non configuré/indisponible."""
    global _client, _tentative_faite
    if _client is not None:
        return _client
    if _tentative_faite:
        return None
    _tentative_faite = True

    url = os.getenv("SUPABASE_URL")
    cle = os.getenv("SUPABASE_KEY")
    if not url or not cle:
        return None

    try:
        from supabase import create_client
        _client = create_client(url, cle)
        return _client
    except Exception:
        return None


def est_configure() -> bool:
    return obtenir_client() is not None


def inserer_departs(departs: list[dict], gare_nom: str, horodatage: str) -> bool:
    """Insère des lignes de départs dans la table 'departures'. False si non configuré."""
    client = obtenir_client()
    if not client:
        return False

    lignes = [
        {
            "horodatage_collecte": horodatage,
            "gare": gare_nom,
            "ligne": d["ligne"],
            "direction": d["direction"],
            "heure_theorique": d["heure_theorique"],
            "heure_prevue": d["heure_prevue"],
            "statut": d["statut"],
        }
        for d in departs
    ]
    if lignes:
        client.table("departures").insert(lignes).execute()
    return True


def charger_departs(limite: int = 5000) -> Optional[list[dict]]:
    """
    Retourne les lignes de la table 'departures', les plus récentes en
    premier, ou None si non configuré.

    Sans tri ni limite explicites, l'API Supabase plafonne silencieusement
    à 1000 lignes (comportement par défaut de PostgREST) : une fois la
    table plus grosse que ça, un simple `select("*")` peut renvoyer un
    sous-ensemble tronqué qui n'inclut plus les lignes les plus récentes,
    ce qui explique un "Dernière collecte" figé et des stats qui semblent
    ne plus se mettre à jour. Trier explicitement par date décroissante
    garantit que les données les plus récentes sont toujours incluses.
    """
    client = obtenir_client()
    if not client:
        return None
    reponse = (
        client.table("departures")
        .select("*")
        .order("horodatage_collecte", desc=True)
        .limit(limite)
        .execute()
    )
    return reponse.data


def charger_dernier_horodatage() -> Optional[str]:
    """Retourne l'horodatage de la ligne la plus récente, sans charger toute la table."""
    client = obtenir_client()
    if not client:
        return None
    reponse = (
        client.table("departures")
        .select("horodatage_collecte")
        .order("horodatage_collecte", desc=True)
        .limit(1)
        .execute()
    )
    return reponse.data[0]["horodatage_collecte"] if reponse.data else None


def alerte_deja_envoyee(cle: str, delai_secondes: int) -> Optional[bool]:
    """None si non configuré, sinon True/False selon si l'alerte est récente."""
    client = obtenir_client()
    if not client:
        return None

    reponse = client.table("alertes_envoyees").select("horodatage").eq("cle", cle).execute()
    if not reponse.data:
        return False
    horodatage = parser_utc_tolerant(reponse.data[0]["horodatage"])
    return (maintenant_utc() - horodatage) < timedelta(seconds=delai_secondes)


def marquer_alerte_envoyee(cle: str) -> bool:
    """Enregistre qu'une alerte vient d'être envoyée, pour la déduplication."""
    client = obtenir_client()
    if not client:
        return False

    client.table("alertes_envoyees").upsert(
        {"cle": cle, "horodatage": maintenant_utc().isoformat()}
    ).execute()
    return True
