"""Fonctions utilitaires de formatage (horaires, affichage)."""

from datetime import datetime

FORMAT_NAVITIA = "%Y%m%dT%H%M%S"


def formater_heure(horaire_navitia: str) -> str:
    if not horaire_navitia:
        return "?"
    dt = datetime.strptime(horaire_navitia, FORMAT_NAVITIA)
    aujourdhui = datetime.now().date()
    if dt.date() == aujourdhui:
        return dt.strftime("%H:%M")
    return dt.strftime("%d/%m à %H:%M")


def calculer_compte_a_rebours(horaire_navitia: str) -> str:
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
