"""Fonctions utilitaires de formatage (horaires, noms de gares, lignes)."""

import re
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


def simplifier_nom_gare(nom: str) -> str:
    """
    Nettoie les noms de lieux renvoyés par l'API SNCF, qui répètent souvent
    la ville en préfixe ET en suffixe entre parenthèses :
    "Paris - Gare de Lyon - Hall 1 & 2 (Paris)" -> "Gare de Lyon - Hall 1 & 2 (Paris)"

    Ne modifie rien si le nom ne suit pas ce motif (ex: pas de parenthèse
    finale, ou pas de préfixe redondant).
    """
    if not nom:
        return nom

    match = re.match(r"^(.+?)\s*\(([^)]+)\)\s*$", nom)
    if not match:
        return nom

    corps, ville = match.group(1).strip(), match.group(2).strip()
    prefixe = f"{ville} - "
    if corps.startswith(prefixe):
        corps = corps[len(prefixe):]

    return f"{corps} ({ville})"


# Lignes Transilien/RER identifiables par leur seule lettre. Les missions
# portent un code du type "P20" (lettre + numéro de train) qui n'est pas
# parlant tel quel pour un usager occasionnel.
NOMS_LIGNES_LETTRES = {
    "A": "RER A", "B": "RER B", "C": "RER C", "D": "RER D", "E": "RER E",
    "H": "Transilien H", "J": "Transilien J", "K": "Transilien K",
    "L": "Transilien L", "N": "Transilien N", "P": "Transilien P",
    "R": "Transilien R", "U": "Transilien U",
}


def humaniser_ligne(code: str, commercial_mode: str | None = None) -> str:
    """
    Transforme un code de ligne/mission brut en nom lisible :
    - lettre seule (ex: "E", "L") -> "RER E", "Transilien L"
    - lettre + numéro de mission, avec suffixe optionnel (ex: "P20", "K1+",
      "K21+") -> "Transilien P", "Transilien K"

    Les libellés déjà complets (ex: "TER 8351", "TGV INOUI 6201") ne
    correspondent à aucun de ces motifs et restent inchangés.

    `commercial_mode` (ex: "RER", "Transilien", "TER", "TGV INOUI", tel que
    renvoyé par l'API) sert de garde-fou : sans lui, on ne peut pas savoir
    si "P20" est un vrai Transilien parisien ou une mission TER en région
    (ex: à Dijon) qui utilise coïncidemment le même format de code. Si
    fourni et que ce n'est manifestement pas un RER/Transilien, on ne
    relabellise pas.
    """
    if not code:
        return code

    code_nettoye = code.strip()

    mode = (commercial_mode or "").strip().lower()
    est_rer_ou_transilien = mode == "" or "rer" in mode or "transilien" in mode

    if re.fullmatch(r"[A-Z]", code_nettoye):
        if est_rer_ou_transilien:
            return NOMS_LIGNES_LETTRES.get(code_nettoye, code)
        return code

    match = re.fullmatch(r"([A-Z])\d{1,3}[A-Z]?\+?", code_nettoye)
    if match:
        if est_rer_ou_transilien:
            return NOMS_LIGNES_LETTRES.get(match.group(1), code)
        return code

    return code
