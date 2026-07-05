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
