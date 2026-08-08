"""Tests pour traincker/i18n.py."""

from traincker.i18n import t


def test_traduction_francais_par_defaut():
    assert t("tab_recherche") == "Recherche"


def test_traduction_anglais():
    assert t("tab_recherche", langue="en") == "Search"


def test_cle_inconnue_retourne_la_cle():
    assert t("cle_qui_n_existe_pas") == "cle_qui_n_existe_pas"


def test_langue_inconnue_replie_sur_francais():
    assert t("tab_recherche", langue="it") == "Recherche"


def test_nouvelles_langues_disponibles():
    assert t("tab_recherche", langue="de") == "Suche"
    assert t("tab_recherche", langue="no") == "Søk"
    assert t("tab_recherche", langue="sv") == "Sök"
