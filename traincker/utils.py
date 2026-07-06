"""Fonctions utilitaires de formatage (horaires, affichage)."""

from datetime import datetime

FORMAT_NAVITIA = "%Y%m%dT%H%M%S"


def formater_heure(horaire_navitia: str) -> str:
    """
    Convertit un horaire brut Navitia (ex: "20260705T144900") en format lisible.

    Retourne "14:49" si c'est aujourd'hui, "05/07 à 14:49" sinon.
    """
    if not horaire_navitia:
        return "?"

    dt = datetime.strptime(horaire_navitia, FORMAT_NAVITIA)
    aujourdhui = datetime.now().date()

    if dt.date() == aujourdhui:
        return dt.strftime("%H:%M")
    return dt.strftime("%d/%m à %H:%M")


def calculer_compte_a_rebours(horaire_navitia: str) -> str:
    """
    Calcule un texte de compte à rebours avant un départ (ex: "12 min", "1h05").

    Retourne "Parti" si l'horaire est dans le passé (au-delà d'une minute de marge).
    """
    if not horaire_navitia:
        return "?"

    dt = datetime.strptime(horaire_navitia, FORMAT_NAVITIA)
    delta_secondes = (dt - datetime.now()).total_seconds()

    if delta_secondes < -60:
        return "Parti"

    minutes = max(0, int(delta_secondes // 60))
    if minutes < 60:
        return f"{minutes} min"

    heures, reste_minutes = divmod(minutes, 60)
    return f"{heures}h{reste_minutes:02d}"
