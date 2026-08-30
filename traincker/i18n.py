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
        "fr": "Mode démo actif, les données affichées sont fictives.",
        "en": "Demo mode active, the data shown is fictional.",
        "de": "Demomodus aktiv, die angezeigten Daten sind fiktiv.",
        "no": "Demomodus aktiv, dataene som vises er fiktive.",
        "sv": "Demoläge aktivt, datan som visas är fiktiv.",
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

    # --- Recherche ---
    "hint_recherche": {
        "fr": "Tape le nom d'une gare (3 caractères minimum) pour voir ses prochains départs.",
        "en": "Type a station name (3 characters minimum) to see its next departures.",
        "de": "Gib einen Bahnhofsnamen ein (mindestens 3 Zeichen), um die nächsten Abfahrten zu sehen.",
        "no": "Skriv inn et stasjonsnavn (minst 3 tegn) for å se neste avganger.",
        "sv": "Skriv in ett stationsnamn (minst 3 tecken) för att se nästa avgångar.",
    },
    "recherches_recentes": {
        "fr": "Recherches récentes", "en": "Recent searches", "de": "Letzte Suchen",
        "no": "Nylige søk", "sv": "Senaste sökningar",
    },
    "continue_a_taper": {
        "fr": "Continue à taper (3 caractères minimum)...", "en": "Keep typing (3 characters minimum)...",
        "de": "Weiter tippen (mindestens 3 Zeichen)...", "no": "Fortsett å skrive (minst 3 tegn)...",
        "sv": "Fortsätt skriva (minst 3 tecken)...",
    },
    "aucun_depart": {
        "fr": "Aucun départ dans l'immédiat.", "en": "No departures in the near future.",
        "de": "Keine unmittelbaren Abfahrten.", "no": "Ingen avganger med det første.",
        "sv": "Inga avgångar inom kort.",
    },
    "aucune_gare_trouvee": {
        "fr": "Aucune gare trouvée.", "en": "No station found.", "de": "Kein Bahnhof gefunden.",
        "no": "Ingen stasjon funnet.", "sv": "Ingen station hittades.",
    },
    "temps_reel": {"fr": "Temps réel", "en": "Live", "de": "Echtzeit", "no": "Sanntid", "sv": "Realtid"},
    "theorique": {"fr": "Théorique", "en": "Scheduled", "de": "Geplant", "no": "Planlagt", "sv": "Planerad"},
    "colonne_ligne": {"fr": "Ligne", "en": "Line", "de": "Linie", "no": "Linje", "sv": "Linje"},
    "colonne_direction": {"fr": "Direction", "en": "Direction", "de": "Richtung", "no": "Retning", "sv": "Riktning"},
    "colonne_depart": {"fr": "Départ", "en": "Departure", "de": "Abfahrt", "no": "Avgang", "sv": "Avgång"},
    "colonne_statut": {"fr": "Statut", "en": "Status", "de": "Status", "no": "Status", "sv": "Status"},

    # --- Favoris ---
    "aucun_favori": {
        "fr": "Aucun trajet favori configuré pour l'instant. Ajoutes-en un ci-dessous.",
        "en": "No favorite route set up yet. Add one below.",
        "de": "Noch keine Lieblingsstrecke eingerichtet. Füge unten eine hinzu.",
        "no": "Ingen favorittrute lagt til ennå. Legg til en under.",
        "sv": "Ingen favoritresa tillagd än. Lägg till en nedan.",
    },
    "desactiver": {"fr": "Désactiver", "en": "Disable", "de": "Deaktivieren", "no": "Deaktiver", "sv": "Inaktivera"},
    "activer": {"fr": "Activer", "en": "Enable", "de": "Aktivieren", "no": "Aktiver", "sv": "Aktivera"},
    "supprimer": {"fr": "Supprimer", "en": "Delete", "de": "Löschen", "no": "Slett", "sv": "Ta bort"},
    "confirmer_suppression": {
        "fr": "Supprimer « {nom} » ? Cette action est irréversible.",
        "en": "Delete \"{nom}\"? This action cannot be undone.",
        "de": "„{nom}“ löschen? Diese Aktion kann nicht rückgängig gemacht werden.",
        "no": "Slette «{nom}»? Denne handlingen kan ikke angres.",
        "sv": "Ta bort \"{nom}\"? Denna åtgärd kan inte ångras.",
    },
    "confirmer": {"fr": "Confirmer", "en": "Confirm", "de": "Bestätigen", "no": "Bekreft", "sv": "Bekräfta"},
    "annuler": {"fr": "Annuler", "en": "Cancel", "de": "Abbrechen", "no": "Avbryt", "sv": "Avbryt"},
    "creer_trajet_retour": {
        "fr": "Créer le trajet retour", "en": "Create the return route", "de": "Rückfahrt erstellen",
        "no": "Opprett returrute", "sv": "Skapa returresa",
    },
    "hint_ajout_favori": {
        "fr": "Cherche une gare de départ et d'arrivée, clique sur une suggestion, puis valide.",
        "en": "Search for a departure and arrival station, click a suggestion, then confirm.",
        "de": "Suche einen Start- und Zielbahnhof, klicke auf einen Vorschlag und bestätige.",
        "no": "Søk etter en avgangs- og ankomststasjon, klikk på et forslag, og bekreft.",
        "sv": "Sök en avgångs- och ankomststation, klicka på ett förslag och bekräfta.",
    },
    "nom_du_trajet": {"fr": "Nom du trajet", "en": "Route name", "de": "Streckenname", "no": "Rutenavn", "sv": "Resans namn"},
    "placeholder_nom_trajet": {
        "fr": "ex: Trajet du matin", "en": "e.g. Morning commute", "de": "z. B. Morgenpendelfahrt",
        "no": "f.eks. Morgenpendling", "sv": "t.ex. Morgonpendling",
    },
    "gare_depart": {"fr": "Gare de départ", "en": "Departure station", "de": "Abfahrtsbahnhof", "no": "Avgangsstasjon", "sv": "Avgångsstation"},
    "gare_arrivee": {"fr": "Gare d'arrivée", "en": "Arrival station", "de": "Ankunftsbahnhof", "no": "Ankomststasjon", "sv": "Ankomststation"},
    "rechercher_min": {
        "fr": "Rechercher (3 car. min.)", "en": "Search (3 char. min.)", "de": "Suchen (mind. 3 Zeichen)",
        "no": "Søk (minst 3 tegn)", "sv": "Sök (minst 3 tecken)",
    },
    "inverser_depart_arrivee": {
        "fr": "Inverser départ / arrivée", "en": "Swap departure / arrival", "de": "Start / Ziel tauschen",
        "no": "Bytt avgang / ankomst", "sv": "Byt avgång / ankomst",
    },
    "depart_selectionne": {
        "fr": "Départ sélectionné : {nom}", "en": "Departure selected: {nom}", "de": "Start ausgewählt: {nom}",
        "no": "Avgang valgt: {nom}", "sv": "Avgång vald: {nom}",
    },
    "arrivee_selectionnee": {
        "fr": "Arrivée sélectionnée : {nom}", "en": "Arrival selected: {nom}", "de": "Ziel ausgewählt: {nom}",
        "no": "Ankomst valgt: {nom}", "sv": "Ankomst vald: {nom}",
    },
    "ajouter_ce_trajet": {"fr": "Ajouter ce trajet", "en": "Add this route", "de": "Strecke hinzufügen", "no": "Legg til rute", "sv": "Lägg till resa"},
    "avertissement_nom_trajet": {
        "fr": "Donne un nom au trajet.", "en": "Give the route a name.", "de": "Gib der Strecke einen Namen.",
        "no": "Gi ruten et navn.", "sv": "Ge resan ett namn.",
    },
    "avertissement_gares_manquantes": {
        "fr": "Cherche et sélectionne une gare de départ ET d'arrivée.",
        "en": "Search and select BOTH a departure and an arrival station.",
        "de": "Suche und wähle sowohl einen Start- als auch einen Zielbahnhof.",
        "no": "Søk og velg både en avgangs- og en ankomststasjon.",
        "sv": "Sök och välj både en avgångs- och en ankomststation.",
    },
    "trajet_ajoute": {
        "fr": "Trajet « {nom} » ajouté !", "en": "Route \"{nom}\" added!", "de": "Strecke „{nom}“ hinzugefügt!",
        "no": "Rute «{nom}» lagt til!", "sv": "Resan \"{nom}\" har lagts till!",
    },
    "trajet_retour_ajoute": {
        "fr": "Trajet retour ajouté.", "en": "Return route added.", "de": "Rückfahrt hinzugefügt.",
        "no": "Returrute lagt til.", "sv": "Returresa tillagd.",
    },
    "favoris_lecture_seule": {
        "fr": "Les trajets favoris affichés sont ceux du propriétaire du site. La modification "
        "est désactivée sur cette démo publique : c'est un aperçu en lecture seule.",
        "en": "The favorite routes shown belong to the site owner. Editing is disabled on this "
        "public demo, this is a read-only preview.",
        "de": "Die angezeigten Lieblingsstrecken gehören dem Website-Betreiber. Das Bearbeiten ist "
        "in dieser öffentlichen Demo deaktiviert, nur zur Ansicht.",
        "no": "Favorittrutene som vises tilhører sideeieren. Redigering er deaktivert i denne "
        "offentlige demoen, kun visning.",
        "sv": "De visade favoritresorna tillhör webbplatsens ägare. Redigering är inaktiverad i "
        "denna offentliga demo, endast för visning.",
    },

    # --- Statistiques ---
    "temps_retard_cumule": {
        "fr": "Temps de retard cumulé", "en": "Cumulative delay", "de": "Kumulierte Verspätung",
        "no": "Akkumulert forsinkelse", "sv": "Ackumulerad försening",
    },
    "tendance_recente": {
        "fr": "Tendance récente", "en": "Recent trend", "de": "Aktueller Trend",
        "no": "Nylig trend", "sv": "Aktuell trend",
    },
    "en_amelioration": {"fr": "En amélioration", "en": "Improving", "de": "Verbessert sich", "no": "Forbedres", "sv": "Förbättras"},
    "en_degradation": {"fr": "En dégradation", "en": "Worsening", "de": "Verschlechtert sich", "no": "Forverres", "sv": "Försämras"},
    "stable": {"fr": "Stable", "en": "Stable", "de": "Stabil", "no": "Stabil", "sv": "Stabil"},
    "pas_assez_de_donnees": {
        "fr": "Pas assez de données", "en": "Not enough data", "de": "Nicht genug Daten",
        "no": "Ikke nok data", "sv": "Inte tillräckligt med data",
    },
    "legende_ponctualite": {
        "fr": "Un train est considéré « à l'heure » s'il part avec moins de 5 minutes de retard.",
        "en": "A train is considered \"on time\" if it departs less than 5 minutes late.",
        "de": "Ein Zug gilt als „pünktlich“, wenn er mit weniger als 5 Minuten Verspätung abfährt.",
        "no": "Et tog anses som «i rute» hvis det avgår med mindre enn 5 minutters forsinkelse.",
        "sv": "Ett tåg anses vara \"i tid\" om det avgår med mindre än 5 minuters försening.",
    },
    "retard_moyen_par_ligne": {
        "fr": "Retard moyen par ligne", "en": "Average delay by line", "de": "Durchschnittliche Verspätung pro Linie",
        "no": "Gjennomsnittlig forsinkelse per linje", "sv": "Genomsnittlig försening per linje",
    },
    "evolution_retard": {
        "fr": "Évolution du retard moyen dans le temps", "en": "Average delay trend over time",
        "de": "Entwicklung der durchschnittlichen Verspätung", "no": "Utvikling av gjennomsnittlig forsinkelse",
        "sv": "Utveckling av genomsnittlig försening",
    },
    "fiabilite_par_gare": {
        "fr": "Fiabilité par gare", "en": "Reliability by station", "de": "Zuverlässigkeit pro Bahnhof",
        "no": "Pålitelighet per stasjon", "sv": "Tillförlitlighet per station",
    },
    "repartition_retards": {
        "fr": "Répartition des retards (jour x heure)", "en": "Delay breakdown (day x hour)",
        "de": "Verspätungsverteilung (Tag x Stunde)", "no": "Forsinkelsesfordeling (dag x time)",
        "sv": "Förseningsfördelning (dag x timme)",
    },
    "pas_assez_pour_cette_vue": {
        "fr": "Pas encore assez de données pour cette vue.", "en": "Not enough data yet for this view.",
        "de": "Noch nicht genug Daten für diese Ansicht.", "no": "Ikke nok data ennå for denne visningen.",
        "sv": "Inte tillräckligt med data ännu för denna vy.",
    },
    "exporter": {"fr": "Exporter", "en": "Export", "de": "Exportieren", "no": "Eksporter", "sv": "Exportera"},
    "export_csv": {"fr": "Export CSV", "en": "Export CSV", "de": "CSV exportieren", "no": "Eksporter CSV", "sv": "Exportera CSV"},
    "export_pdf": {"fr": "Export PDF", "en": "Export PDF", "de": "PDF exportieren", "no": "Eksporter PDF", "sv": "Exportera PDF"},
    "aide_ponctualite": {
        "fr": "Part des trains partis avec moins de 5 min de retard", "en": "Share of trains that left less than 5 min late",
        "de": "Anteil der Züge mit weniger als 5 Min. Verspätung", "no": "Andel tog som gikk med mindre enn 5 min forsinkelse",
        "sv": "Andel tåg som avgick med mindre än 5 min försening",
    },
    "aide_retard_moyen": {
        "fr": "Retard moyen constaté sur la ligne", "en": "Average observed delay on this line",
        "de": "Durchschnittlich beobachtete Verspätung auf dieser Linie", "no": "Gjennomsnittlig observert forsinkelse på linjen",
        "sv": "Genomsnittlig observerad försening på linjen",
    },
    "aide_regularite": {
        "fr": "Écart-type du retard : plus c'est bas, plus la ligne est régulière",
        "en": "Delay standard deviation: the lower, the more consistent the line",
        "de": "Standardabweichung der Verspätung: je niedriger, desto regelmäßiger die Linie",
        "no": "Standardavvik for forsinkelse: jo lavere, jo mer regelmessig linjen",
        "sv": "Standardavvikelse för försening: ju lägre, desto jämnare linje",
    },
    "aide_trains_observes": {
        "fr": "Nombre de départs historisés pour cette ligne", "en": "Number of recorded departures for this line",
        "de": "Anzahl der aufgezeichneten Abfahrten für diese Linie", "no": "Antall registrerte avganger for denne linjen",
        "sv": "Antal registrerade avgångar för denna linje",
    },
    "stats_vide": {
        "fr": "Pas encore assez de données exploitables pour calculer des stats.",
        "en": "Not enough usable data yet to compute statistics.",
        "de": "Noch nicht genug nutzbare Daten für Statistiken.",
        "no": "Ikke nok brukbare data ennå for å beregne statistikk.",
        "sv": "Inte tillräckligt med användbar data för att beräkna statistik.",
    },
    "stats_hint_vide": {
        "fr": "Aucune donnée historisée pour l'instant. Lance `python main.py surveiller` "
        "un moment pour commencer à collecter des données.",
        "en": "No historical data yet. Run `python main.py surveiller` for a while "
        "to start collecting data.",
        "de": "Noch keine historischen Daten. Führe `python main.py surveiller` eine "
        "Weile aus, um Daten zu sammeln.",
        "no": "Ingen historiske data ennå. Kjør `python main.py surveiller` en "
        "stund for å begynne å samle data.",
        "sv": "Ingen historisk data ännu. Kör `python main.py surveiller` ett "
        "tag för att börja samla in data.",
    },
    "voir_code_github": {
        "fr": "Voir le code sur GitHub", "en": "View the code on GitHub", "de": "Code auf GitHub ansehen",
        "no": "Se koden på GitHub", "sv": "Se koden på GitHub",
    },
    "fichier_invalide": {
        "fr": "Fichier invalide : {erreur}", "en": "Invalid file: {erreur}", "de": "Ungültige Datei: {erreur}",
        "no": "Ugyldig fil: {erreur}", "sv": "Ogiltig fil: {erreur}",
    },
    "export_import_desactives": {
        "fr": "Export/import désactivés sur cette démo publique.",
        "en": "Export/import disabled on this public demo.",
        "de": "Export/Import in dieser öffentlichen Demo deaktiviert.",
        "no": "Eksport/import deaktivert i denne offentlige demoen.",
        "sv": "Export/import inaktiverat i denna offentliga demo.",
    },
    "restaurer": {"fr": "Restaurer", "en": "Restore", "de": "Wiederherstellen", "no": "Gjenopprett", "sv": "Återställ"},
    "trajets_restaures": {
        "fr": "{n} trajet(s) restauré(s).", "en": "{n} route(s) restored.", "de": "{n} Strecke(n) wiederhergestellt.",
        "no": "{n} rute(r) gjenopprettet.", "sv": "{n} resa(or) återställda.",
    },
    "journal_type_recherche": {"fr": "Recherche", "en": "Search", "de": "Suche", "no": "Søk", "sv": "Sökning"},
    "journal_type_ajout_favori": {
        "fr": "Trajet ajouté", "en": "Route added", "de": "Strecke hinzugefügt",
        "no": "Rute lagt til", "sv": "Resa tillagd",
    },
}


def t(cle: str, langue: str = "fr") -> str:
    """Retourne le texte traduit pour une clé donnée, avec repli sur le français."""
    entree = TRADUCTIONS.get(cle)
    if not entree:
        return cle
    return entree.get(langue, entree["fr"])


def formatter(cle: str, langue: str = "fr", **kwargs) -> str:
    """Comme t(), mais interpole des variables dans le texte (ex: {nom})."""
    texte = t(cle, langue)
    try:
        return texte.format(**kwargs)
    except (KeyError, IndexError):
        return texte
