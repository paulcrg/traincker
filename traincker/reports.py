"""Génération et envoi du rapport hebdomadaire de ponctualité par email."""

from traincker.tz_utils import maintenant_paris
from traincker.analysis import (
    charger_donnees, stats_ponctualite_par_ligne, generer_synthese,
    temps_perdu_cumule_minutes, detecter_tendance,
)
from traincker.alerts import send_email_alert
from traincker.settings import charger_parametres

LIBELLES_TENDANCE = {"amelioration": "en amélioration", "degradation": "en dégradation", "stable": "stable"}


def generer_rapport_texte() -> str:
    try:
        df = charger_donnees()
    except FileNotFoundError:
        return "Aucune donnée historisée pour le moment."

    if df.empty:
        return "Aucune donnée exploitable pour le moment."

    stats = stats_ponctualite_par_ligne(df)
    synthese = generer_synthese(stats)
    temps_perdu = temps_perdu_cumule_minutes(df)
    tendance = detecter_tendance(df)

    lignes = [f"Rapport Traincker - semaine du {maintenant_paris():%d/%m/%Y}", "", synthese]
    lignes.append(f"\nTemps de retard cumulé observé : {temps_perdu:.0f} minutes.")

    if tendance:
        libelle = LIBELLES_TENDANCE.get(tendance["direction"], tendance["direction"])
        lignes.append(f"Tendance récente : {libelle} ({tendance['variation_minutes']:+.1f} min vs période précédente).")

    return "\n".join(lignes)


def envoyer_rapport_hebdomadaire() -> bool:
    parametres = charger_parametres()
    destinataire = parametres.get("email_destinataire")
    if not parametres.get("canal_email") or not destinataire:
        print("Rapport hebdomadaire ignoré : email non configuré.")
        return False

    rapport = generer_rapport_texte()
    send_email_alert("Traincker - Rapport hebdomadaire", rapport, destinataire)
    print("Rapport hebdomadaire envoyé par email.")
    return True
