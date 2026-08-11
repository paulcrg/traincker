"""
Utilitaires de fuseau horaire.

GitHub Actions et Render tournent en UTC, alors que les heures configurées
par l'utilisateur (silence, affichage) sont pensées en heure française.
Sans conversion explicite, tout ce qui est écrit/lu sur ces plateformes
apparaît décalé de 1h (hiver) ou 2h (été) par rapport à l'heure réelle.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

FUSEAU_PARIS = ZoneInfo("Europe/Paris")


def maintenant_utc() -> datetime:
    return datetime.now(timezone.utc)


def maintenant_paris() -> datetime:
    return datetime.now(timezone.utc).astimezone(FUSEAU_PARIS)


def vers_paris(dt: datetime) -> datetime:
    """Convertit un datetime vers l'heure de Paris. Suppose UTC si naïf."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(FUSEAU_PARIS)


def parser_horodatage_affichage(valeur) -> datetime:
    """
    Parse un horodatage stocké (str ISO ou datetime) pour l'affichage.
    Un horodatage "aware" (avec fuseau, ex: venant de Supabase/UTC) est
    converti en heure de Paris. Un horodatage naïf (ancien fichier local,
    déjà en heure locale de la machine) est laissé tel quel.
    """
    dt = datetime.fromisoformat(valeur) if isinstance(valeur, str) else valeur
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(FUSEAU_PARIS)


def parser_utc_tolerant(valeur: str) -> datetime:
    """Parse un ISO stocké pour un calcul de delta. Suppose UTC si naïf
    (compatibilité avec d'anciennes entrées écrites avant ce correctif)."""
    dt = datetime.fromisoformat(valeur)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt
