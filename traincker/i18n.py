"""
Traductions pour les éléments principaux de l'interface : FR, EN, DE, NO, SV.

Couvre la structure du dashboard (titres, onglets, boutons, libellés
courants). Le contenu généré dynamiquement (noms de gares, messages
d'erreur API bruts, changelog, journal) reste en français pour l'instant.
"""

TRADUCTIONS = {
    "caption": {
        "fr": "Suivi de trains au quotidien", "en": "Daily train tracking",
        "de": "Tägliche Zugverfolgung", "no": "Daglig togsporing", "sv": "Daglig tågspårning",
    },
    "tab_recherche": {
        "fr": "Recherche", "en": "Search", "de": "Suche", "no": "Søk", "sv": "Sök",
    },
    "tab_favoris": {
        "fr": "Mes trajets favoris", "en": "My favorite routes", "de": "Meine Strecken",
        "no": "Mine favorittruter", "sv": "Mina favoritresor",
    },
    "tab_stats": {
        "fr": "Statistiques", "en": "Statistics", "de": "Statistiken",
        "no": "Statistikk", "sv": "Statistik",
    },
    "tab_apropos": {
        "fr": "En savoir plus", "en": "About", "de": "Mehr erfahren",
        "no": "Mer informasjon", "sv": "Mer information",
    },
    "chip_trajets_actifs": {
        "fr": "Trajets actifs", "en": "Active routes", "de": "Aktive Strecken",
        "no": "Aktive ruter", "sv": "Aktiva resor",
    },
    "chip_derniere_collecte": {
        "fr": "Dernière collecte", "en": "Last update", "de": "Letzte Aktualisierung",
        "no": "Siste oppdatering", "sv": "Senaste uppdatering",
    },
    "chip_alertes": {
        "fr": "Alertes envoyées", "en": "Alerts sent", "de": "Gesendete Warnungen",
        "no": "Sendte varsler", "sv": "Skickade varningar",
    },
    "prochains_departs": {
        "fr": "Prochains départs", "en": "Next departures", "de": "Nächste Abfahrten",
        "no": "Neste avganger", "sv": "Nästa avgångar",
    },
    "rafraichir": {
        "fr": "Rafraîchir", "en": "Refresh", "de": "Aktualisieren",
        "no": "Oppdater", "sv": "Uppdatera",
    },
    "trajets_favoris": {
        "fr": "Trajets favoris", "en": "Favorite routes", "de": "Lieblingsstrecken",
        "no": "Favorittruter", "sv": "Favoritresor",
    },
    "ajouter_trajet": {
        "fr": "Ajouter un trajet favori", "en": "Add a favorite route",
        "de": "Strecke hinzufügen", "no": "Legg til favorittrute", "sv": "Lägg till favoritresa",
    },
    "nom_trajet": {
        "fr": "Nom du trajet", "en": "Route name", "de": "Streckenname",
        "no": "Rutenavn", "sv": "Resans namn",
    },
    "gare_depart": {
        "fr": "Gare de départ", "en": "Departure station", "de": "Abfahrtsbahnhof",
        "no": "Avgangsstasjon", "sv": "Avgångsstation",
    },
    "gare_arrivee": {
        "fr": "Gare d'arrivée", "en": "Arrival station", "de": "Ankunftsbahnhof",
        "no": "Ankomststasjon", "sv": "Ankomststation",
    },
    "ajouter_ce_trajet": {
        "fr": "Ajouter ce trajet", "en": "Add this route", "de": "Strecke hinzufügen",
        "no": "Legg til rute", "sv": "Lägg till resa",
    },
    "desactiver": {
        "fr": "Désactiver", "en": "Disable", "de": "Deaktivieren",
        "no": "Deaktiver", "sv": "Inaktivera",
    },
    "activer": {
        "fr": "Activer", "en": "Enable", "de": "Aktivieren", "no": "Aktiver", "sv": "Aktivera",
    },
    "supprimer": {
        "fr": "Supprimer", "en": "Delete", "de": "Löschen", "no": "Slett", "sv": "Ta bort",
    },
    "statistiques_ponctualite": {
        "fr": "Statistiques de ponctualité", "en": "Punctuality statistics",
        "de": "Pünktlichkeitsstatistik", "no": "Punktlighetsstatistikk", "sv": "Punktlighetsstatistik",
    },
    "parametres_alerte": {
        "fr": "Paramètres d'alerte", "en": "Alert settings", "de": "Warneinstellungen",
        "no": "Varselinnstillinger", "sv": "Varningsinställningar",
    },
    "accessibilite": {
        "fr": "Accessibilité", "en": "Accessibility", "de": "Barrierefreiheit",
        "no": "Tilgjengelighet", "sv": "Tillgänglighet",
    },
    "mon_historique": {
        "fr": "Mon historique", "en": "My history", "de": "Mein Verlauf",
        "no": "Min historikk", "sv": "Min historik",
    },
    "journal_technique": {
        "fr": "Journal technique", "en": "Technical log", "de": "Technisches Protokoll",
        "no": "Teknisk logg", "sv": "Teknisk logg",
    },
    "un_probleme": {
        "fr": "Un problème ?", "en": "Something wrong?", "de": "Ein Problem?",
        "no": "Et problem?", "sv": "Ett problem?",
    },
    "signaler_bug": {
        "fr": "Signaler un bug sur GitHub", "en": "Report a bug on GitHub",
        "de": "Fehler auf GitHub melden", "no": "Meld en feil på GitHub", "sv": "Rapportera ett fel på GitHub",
    },
    "mode_demo": {
        "fr": "Mode démo (données fictives)", "en": "Demo mode (fake data)",
        "de": "Demomodus (fiktive Daten)", "no": "Demomodus (fiktive data)", "sv": "Demoläge (fiktiv data)",
    },
    "langue": {
        "fr": "Langue", "en": "Language", "de": "Sprache", "no": "Språk", "sv": "Språk",
    },
    "theme_clair": {
        "fr": "Thème clair", "en": "Light theme", "de": "Helles Design",
        "no": "Lyst tema", "sv": "Ljust tema",
    },
    "applique_immediat": {
        "fr": "Ces réglages s'appliquent immédiatement.",
        "en": "These settings apply immediately.",
        "de": "Diese Einstellungen werden sofort angewendet.",
        "no": "Disse innstillingene gjelder umiddelbart.",
        "sv": "Dessa inställningar tillämpas omedelbart.",
    },
    "contraste_eleve_label": {
        "fr": "Contraste élevé", "en": "High contrast", "de": "Hoher Kontrast",
        "no": "Høy kontrast", "sv": "Hög kontrast",
    },
    "taille_texte": {
        "fr": "Taille du texte", "en": "Text size", "de": "Textgröße",
        "no": "Tekststørrelse", "sv": "Textstorlek",
    },
    "taille_normale": {
        "fr": "Normale", "en": "Normal", "de": "Normal", "no": "Normal", "sv": "Normal",
    },
    "taille_grande": {
        "fr": "Grande", "en": "Large", "de": "Groß", "no": "Stor", "sv": "Stor",
    },
    "taille_tres_grande": {
        "fr": "Très grande", "en": "Very large", "de": "Sehr groß",
        "no": "Svært stor", "sv": "Mycket stor",
    },
    "mode_demo_actif": {
        "fr": "Mode démo actif — les données affichées sont fictives.",
        "en": "Demo mode active — the data shown is fictional.",
        "de": "Demomodus aktiv — die angezeigten Daten sind fiktiv.",
        "no": "Demomodus aktiv — dataene som vises er fiktive.",
        "sv": "Demoläge aktivt — datan som visas är fiktiv.",
    },
    "aucune_perturbation": {
        "fr": "Aucune perturbation signalée", "en": "No disruption reported",
        "de": "Keine Störung gemeldet", "no": "Ingen forstyrrelser rapportert",
        "sv": "Inga störningar rapporterade",
    },
    "perturbations_en_cours": {
        "fr": "Perturbations en cours", "en": "Ongoing disruptions",
        "de": "Aktuelle Störungen", "no": "Pågående forstyrrelser", "sv": "Pågående störningar",
    },
}


def t(cle: str, langue: str = "fr") -> str:
    """Retourne le texte traduit pour une clé donnée, avec repli sur le français."""
    entree = TRADUCTIONS.get(cle)
    if not entree:
        return cle
    return entree.get(langue, entree["fr"])
