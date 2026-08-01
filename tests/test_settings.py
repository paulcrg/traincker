"""Tests pour traincker/settings.py."""

from traincker.settings import charger_parametres, sauvegarder_parametres, DEFAUTS


def test_charger_parametres_defauts_si_fichier_absent(tmp_path):
    parametres = charger_parametres(path=tmp_path / "inexistant.json")
    assert parametres == DEFAUTS


def test_sauvegarder_puis_charger_parametres(tmp_path):
    path = tmp_path / "parametres.json"
    perso = DEFAUTS.copy()
    perso["silence_debut"] = "23:00"
    perso["canal_email"] = True
    perso["email_destinataire"] = "paul@example.com"

    sauvegarder_parametres(perso, path=path)
    relu = charger_parametres(path=path)

    assert relu["silence_debut"] == "23:00"
    assert relu["canal_email"] is True
    assert relu["email_destinataire"] == "paul@example.com"


def test_charger_parametres_complete_les_champs_manquants(tmp_path):
    path = tmp_path / "parametres.json"
    sauvegarder_parametres({"silence_debut": "21:00"}, path=path)
    relu = charger_parametres(path=path)

    assert relu["silence_debut"] == "21:00"
    assert relu["silence_fin"] == DEFAUTS["silence_fin"]
