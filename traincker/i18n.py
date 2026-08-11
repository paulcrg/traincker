"""
Traductions pour les éléments principaux de l'interface : FR, EN, DE, NO, SV.

Couvre la structure du dashboard (titres, onglets, boutons, libellés
courants). Le contenu authored par l'utilisateur (description du projet,
changelog, noms de gares) reste en français.
"""

TRADUCTIONS = {
    "caption": {
        "fr": "Suivi de trains au quotidien", "en": "Daily train tracking",
        "de": "Tägliche Zugverfolgung", "no": "Daglig togsporing", "sv": "Daglig tågspårning",
    },
    "tab_recherche": {"fr": "Recherche", "en": "Search", "de": "Suche", "no": "Søk", "sv": "Sök"},
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
    "statistiques_ponctualite": {
        "fr": "Statistiques de ponctualité", "en": "Punctuality statistics",
        "de": "Pünktlichkeitsstatistik", "no": "Punktlighetsstatistikk", "sv": "Punktlighetsstatistik",
    },
    "un_probleme": {
        "fr": "Un problème ?", "en": "Something wrong?", "de": "Ein Problem?",
        "no": "Et problem?", "sv": "Ett problem?",
    },
    "signaler_bug": {
        "fr": "Signaler un bug sur GitHub", "en": "Report a bug on GitHub",
        "de": "Fehler auf GitHub melden", "no": "Meld en feil på GitHub", "sv": "Rapportera ett fel på GitHub",
    },
    "langue": {"fr": "Langue", "en": "Language", "de": "Sprache", "no": "Språk", "sv": "Språk"},
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
    "accessibilite": {
        "fr": "Accessibilité", "en": "Accessibility", "de": "Barrierefreiheit",
        "no": "Tilgjengelighet", "sv": "Tillgänglighet",
    },
    "contraste_eleve_label": {
        "fr": "Contraste élevé", "en": "High contrast", "de": "Hoher Kontrast",
        "no": "Høy kontrast", "sv": "Hög kontrast",
    },
    "taille_texte": {
        "fr": "Taille du texte", "en": "Text size", "de": "Textgröße",
        "no": "Tekststørrelse", "sv": "Textstorlek",
    },
    "taille_normale": {"fr": "Normale", "en": "Normal", "de": "Normal", "no": "Normal", "sv": "Normal"},
    "taille_grande": {"fr": "Grande", "en": "Large", "de": "Groß", "no": "Stor", "sv": "Stor"},
    "taille_tres_grande": {
        "fr": "Très grande", "en": "Very large", "de": "Sehr groß", "no": "Svært stor", "sv": "Mycket stor",
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
        "de": "Keine Störung gemeldet", "no": "Ingen forstyrrelser rapportert", "sv": "Inga störningar rapporterade",
    },
    "perturbations_en_cours": {
        "fr": "Perturbations en cours", "en": "Ongoing disruptions",
        "de": "Aktuelle Störungen", "no": "Pågående forstyrrelser", "sv": "Pågående störningar",
    },
    "mon_historique": {
        "fr": "Mon historique", "en": "My history", "de": "Mein Verlauf",
        "no": "Min historikk", "sv": "Min historik",
    },
    "historique_hint": {
        "fr": "Trace de tes recherches et trajets ajoutés au fil du temps.",
        "en": "Trace of your searches and routes added over time.",
        "de": "Verlauf deiner Suchen und hinzugefügten Strecken.",
        "no": "Spor av søkene og rutene dine over tid.",
        "sv": "Spår av dina sökningar och tillagda resor över tid.",
    },
    "historique_vide": {
        "fr": "Aucune activité enregistrée pour l'instant.", "en": "No activity recorded yet.",
        "de": "Noch keine Aktivität aufgezeichnet.", "no": "Ingen aktivitet registrert ennå.",
        "sv": "Ingen aktivitet registrerad än.",
    },
    "vider_historique": {
        "fr": "Vider mon historique", "en": "Clear my history", "de": "Verlauf löschen",
        "no": "Tøm historikken min", "sv": "Rensa min historik",
    },
    "journal_technique": {
        "fr": "Journal technique", "en": "Technical log", "de": "Technisches Protokoll",
        "no": "Teknisk logg", "sv": "Teknisk logg",
    },
    "journal_hint": {
        "fr": "Erreurs et événements techniques, utile pour diagnostiquer un souci sans terminal.",
        "en": "Errors and technical events, useful for troubleshooting without a terminal.",
        "de": "Fehler und technische Ereignisse zur Fehlerdiagnose ohne Terminal.",
        "no": "Feil og tekniske hendelser, nyttig for feilsøking uten terminal.",
        "sv": "Fel och tekniska händelser, användbart för felsökning utan terminal.",
    },
    "aucun_evenement": {
        "fr": "Aucun événement enregistré.", "en": "No event recorded.",
        "de": "Kein Ereignis aufgezeichnet.", "no": "Ingen hendelse registrert.", "sv": "Ingen händelse registrerad.",
    },
    "vider_logs": {
        "fr": "Vider les logs", "en": "Clear logs", "de": "Protokoll leeren",
        "no": "Tøm loggen", "sv": "Rensa loggen",
    },
    "parametres_alerte": {
        "fr": "Paramètres d'alerte", "en": "Alert settings", "de": "Warneinstellungen",
        "no": "Varselinnstillinger", "sv": "Varningsinställningar",
    },
    "parametres_alerte_hint": {
        "fr": "S'applique à la surveillance en arrière-plan.",
        "en": "Applies to the background monitoring.",
        "de": "Gilt für die Hintergrundüberwachung.",
        "no": "Gjelder for bakgrunnsovervåking.",
        "sv": "Gäller för bakgrundsövervakningen.",
    },
    "silence_a_partir_de": {
        "fr": "Silence à partir de", "en": "Quiet from", "de": "Ruhe ab",
        "no": "Stille fra", "sv": "Tyst från",
    },
    "silence_jusqua": {
        "fr": "Silence jusqu'à", "en": "Quiet until", "de": "Ruhe bis",
        "no": "Stille til", "sv": "Tyst till",
    },
    "note_perturbations_critiques": {
        "fr": "Les perturbations critiques (suppression de service) passent toujours.",
        "en": "Critical disruptions (service cancellations) always come through.",
        "de": "Kritische Störungen (Ausfälle) werden immer gesendet.",
        "no": "Kritiske forstyrrelser (innstilte avganger) sendes alltid.",
        "sv": "Kritiska störningar (inställda avgångar) skickas alltid.",
    },
    "alertes_discord_label": {
        "fr": "Alertes Discord", "en": "Discord alerts", "de": "Discord-Benachrichtigungen",
        "no": "Discord-varsler", "sv": "Discord-varningar",
    },
    "alertes_email_label": {
        "fr": "Alertes email", "en": "Email alerts", "de": "E-Mail-Benachrichtigungen",
        "no": "E-postvarsler", "sv": "E-postvarningar",
    },
    "adresse_email_label": {
        "fr": "Adresse email de destination", "en": "Recipient email address",
        "de": "Empfänger-E-Mail-Adresse", "no": "Mottakerens e-postadresse", "sv": "Mottagarens e-postadress",
    },
    "alertes_meteo_label": {
        "fr": "Alertes météo (neige, orage, pluie forte)",
        "en": "Weather alerts (snow, storm, heavy rain)",
        "de": "Wetterwarnungen (Schnee, Gewitter, Starkregen)",
        "no": "Værvarsler (snø, uvær, kraftig regn)",
        "sv": "Vädervarningar (snö, åska, kraftigt regn)",
    },
    "enregistrer_parametres": {
        "fr": "Enregistrer les paramètres", "en": "Save settings", "de": "Einstellungen speichern",
        "no": "Lagre innstillinger", "sv": "Spara inställningar",
    },
    "note_rapport_hebdo": {
        "fr": "Un rapport de ponctualité est envoyé automatiquement chaque lundi à 8h "
        "si les alertes email sont activées. Tu peux aussi le tester manuellement :",
        "en": "A punctuality report is sent automatically every Monday at 8am "
        "if email alerts are enabled. You can also test it manually:",
        "de": "Ein Pünktlichkeitsbericht wird automatisch jeden Montag um 8 Uhr "
        "gesendet, wenn E-Mail-Benachrichtigungen aktiviert sind. Du kannst ihn auch manuell testen:",
        "no": "En punktlighetsrapport sendes automatisk hver mandag kl. 8 hvis "
        "e-postvarsler er aktivert. Du kan også teste den manuelt:",
        "sv": "En punktlighetsrapport skickas automatiskt varje måndag kl. 8 om "
        "e-postvarningar är aktiverade. Du kan också testa den manuellt:",
    },
    "envoyer_rapport": {
        "fr": "Envoyer le rapport hebdomadaire maintenant", "en": "Send the weekly report now",
        "de": "Wöchentlichen Bericht jetzt senden", "no": "Send ukerapporten nå", "sv": "Skicka veckorapporten nu",
    },
    "sauvegarde_config_title": {
        "fr": "Sauvegarde de la configuration", "en": "Configuration backup",
        "de": "Konfigurationssicherung", "no": "Sikkerhetskopiering av konfigurasjon",
        "sv": "Säkerhetskopiering av konfiguration",
    },
    "sauvegarde_config_hint": {
        "fr": "Exporte tes trajets favoris pour les garder en sécurité, ou restaure une sauvegarde précédente.",
        "en": "Export your favorite routes to keep them safe, or restore a previous backup.",
        "de": "Exportiere deine Lieblingsstrecken oder stelle eine frühere Sicherung wieder her.",
        "no": "Eksporter favorittrutene dine, eller gjenopprett en tidligere sikkerhetskopi.",
        "sv": "Exportera dina favoritresor, eller återställ en tidigare säkerhetskopia.",
    },
    "exporter_trajets": {
        "fr": "Exporter mes trajets", "en": "Export my routes", "de": "Strecken exportieren",
        "no": "Eksporter rutene mine", "sv": "Exportera mina resor",
    },
    "confirmer_restauration": {
        "fr": "Confirmer la restauration", "en": "Confirm restore", "de": "Wiederherstellung bestätigen",
        "no": "Bekreft gjenoppretting", "sv": "Bekräfta återställning",
    },
    "vue_technique": {
        "fr": "Vue technique", "en": "Technical overview", "de": "Technische Übersicht",
        "no": "Teknisk oversikt", "sv": "Teknisk översikt",
    },
    "historique_evolutions": {
        "fr": "Historique des évolutions", "en": "Changelog", "de": "Änderungsprotokoll",
        "no": "Endringslogg", "sv": "Ändringslogg",
    },
    "en_savoir_plus_titre": {
        "fr": "En savoir plus sur le projet", "en": "More about the project",
        "de": "Mehr über das Projekt", "no": "Mer om prosjektet", "sv": "Mer om projektet",
    },
}


def t(cle: str, langue: str = "fr") -> str:
    """Retourne le texte traduit pour une clé donnée, avec repli sur le français."""
    entree = TRADUCTIONS.get(cle)
    if not entree:
        return cle
    return entree.get(langue, entree["fr"])
