"""Tests pour les nouvelles préférences d'accessibilité dans settings.py."""

from traincker.settings import charger_parametres, DEFAUTS


def test_defauts_incluent_accessibilite():
    assert DEFAUTS["contraste_eleve"] is False
    assert DEFAUTS["taille_police"] == "normale"


def test_charger_parametres_ancien_fichier_sans_accessibilite(tmp_path):
    import json
    path = tmp_path / "parametres.json"
    path.write_text(json.dumps({"silence_debut": "23:00"}), encoding="utf-8")

    parametres = charger_parametres(path=path)
    assert parametres["contraste_eleve"] is False
    assert parametres["taille_police"] == "normale"
    assert parametres["silence_debut"] == "23:00"
