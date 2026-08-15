"""Tests pour traincker/utils.py."""

from traincker.utils import (
    formater_heure,
    calculer_compte_a_rebours,
    simplifier_nom_gare,
    humaniser_ligne,
)


def test_formater_heure_vide():
    assert formater_heure("") == "?"
    assert formater_heure(None) == "?"


def test_compte_a_rebours_vide():
    assert calculer_compte_a_rebours("") == "?"


def test_simplifier_nom_gare_prefixe_redondant():
    assert (
        simplifier_nom_gare("Paris - Gare de Lyon - Hall 1 & 2 (Paris)")
        == "Gare de Lyon - Hall 1 & 2 (Paris)"
    )


def test_simplifier_nom_gare_sans_redondance_inchange():
    assert simplifier_nom_gare("Dijon Ville") == "Dijon Ville"


def test_simplifier_nom_gare_vide():
    assert simplifier_nom_gare("") == ""
    assert simplifier_nom_gare(None) is None


def test_humaniser_ligne_mission_avec_numero():
    assert humaniser_ligne("P20") == "Transilien P"
    assert humaniser_ligne("A5") == "RER A"


def test_humaniser_ligne_lettre_seule():
    assert humaniser_ligne("E") == "RER E"
    assert humaniser_ligne("J") == "Transilien J"
    assert humaniser_ligne("L") == "Transilien L"


def test_humaniser_ligne_avec_suffixe_plus():
    assert humaniser_ligne("K1+") == "Transilien K"
    assert humaniser_ligne("K21+") == "Transilien K"
    assert humaniser_ligne("K3+") == "Transilien K"


def test_humaniser_ligne_deja_complete_inchangee():
    assert humaniser_ligne("TER 8351") == "TER 8351"
    assert humaniser_ligne("TGV INOUI 6201") == "TGV INOUI 6201"


def test_humaniser_ligne_vide():
    assert humaniser_ligne("") == ""
    assert humaniser_ligne(None) is None
