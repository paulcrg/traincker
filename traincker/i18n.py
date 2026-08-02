"""
Traductions FR/EN pour les éléments principaux de l'interface.

Couvre la structure du dashboard (titres, onglets, boutons courants).
Le contenu généré dynamiquement (noms de gares, messages d'erreur API,
CHANGELOG) reste en français pour l'instant.
"""

TRADUCTIONS = {
    "caption": {"fr": "Suivi de trains au quotidien", "en": "Daily train tracking"},
    "tab_recherche": {"fr": "Recherche", "en": "Search"},
    "tab_favoris": {"fr": "Mes trajets favoris", "en": "My favorite routes"},
    "tab_stats": {"fr": "Statistiques", "en": "Statistics"},
    "tab_apropos": {"fr": "En savoir plus", "en": "About"},
    "chip_trajets_actifs": {"fr": "Trajets actifs", "en": "Active routes"},
    "chip_derniere_collecte": {"fr": "Dernière collecte", "en": "Last update"},
    "chip_alertes": {"fr": "Alertes envoyées", "en": "Alerts sent"},
    "prochains_departs": {"fr": "Prochains départs", "en": "Next departures"},
    "rafraichir": {"fr": "Rafraîchir", "en": "Refresh"},
    "trajets_favoris": {"fr": "Trajets favoris", "en": "Favorite routes"},
    "ajouter_trajet": {"fr": "Ajouter un trajet favori", "en": "Add a favorite route"},
    "nom_trajet": {"fr": "Nom du trajet", "en": "Route name"},
    "gare_depart": {"fr": "Gare de départ", "en": "Departure station"},
    "gare_arrivee": {"fr": "Gare d'arrivée", "en": "Arrival station"},
    "ajouter_ce_trajet": {"fr": "Ajouter ce trajet", "en": "Add this route"},
    "desactiver": {"fr": "Désactiver", "en": "Disable"},
    "activer": {"fr": "Activer", "en": "Enable"},
    "supprimer": {"fr": "Supprimer", "en": "Delete"},
    "statistiques_ponctualite": {"fr": "Statistiques de ponctualité", "en": "Punctuality statistics"},
    "parametres_alerte": {"fr": "Paramètres d'alerte", "en": "Alert settings"},
    "accessibilite": {"fr": "Accessibilité", "en": "Accessibility"},
    "mon_historique": {"fr": "Mon historique", "en": "My history"},
    "journal_technique": {"fr": "Journal technique", "en": "Technical log"},
    "un_probleme": {"fr": "Un problème ?", "en": "Something wrong?"},
    "signaler_bug": {"fr": "Signaler un bug sur GitHub", "en": "Report a bug on GitHub"},
    "mode_demo": {"fr": "Mode démo (données fictives)", "en": "Demo mode (fake data)"},
    "langue": {"fr": "Langue", "en": "Language"},
    "theme_clair": {"fr": "Thème clair", "en": "Light theme"},
}


def t(cle: str, langue: str = "fr") -> str:
    """Retourne le texte traduit pour une clé donnée, avec repli sur le français."""
    entree = TRADUCTIONS.get(cle)
    if not entree:
        return cle
    return entree.get(langue, entree["fr"])
