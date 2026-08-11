"""Tests pour traincker/tz_utils.py."""

from datetime import datetime, timezone

from traincker.tz_utils import (
    vers_paris,
    parser_horodatage_affichage,
    parser_utc_tolerant,
    FUSEAU_PARIS,
)


def test_vers_paris_en_ete_utc_plus_2():
    dt_utc = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
    dt_paris = vers_paris(dt_utc)
    assert dt_paris.hour == 14  # UTC+2 en été (CEST)


def test_vers_paris_en_hiver_utc_plus_1():
    dt_utc = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
    dt_paris = vers_paris(dt_utc)
    assert dt_paris.hour == 13  # UTC+1 en hiver (CET)


def test_vers_paris_suppose_utc_si_naif():
    dt_naif = datetime(2026, 7, 15, 12, 0)
    dt_paris = vers_paris(dt_naif)
    assert dt_paris.hour == 14


def test_parser_horodatage_affichage_aware_convertit():
    iso = "2026-07-15T12:00:00+00:00"
    dt = parser_horodatage_affichage(iso)
    assert dt.hour == 14
    assert dt.tzinfo is not None


def test_parser_horodatage_affichage_naif_inchange():
    iso = "2026-07-15T12:00:00"
    dt = parser_horodatage_affichage(iso)
    assert dt.hour == 12  # pas de conversion, supposé déjà en heure locale


def test_parser_utc_tolerant_avec_ancienne_entree_naive():
    dt = parser_utc_tolerant("2026-07-15T12:00:00")
    assert dt.tzinfo is not None  # tagué UTC pour permettre les comparaisons


def test_parser_utc_tolerant_avec_entree_deja_aware():
    dt = parser_utc_tolerant("2026-07-15T12:00:00+00:00")
    assert dt.tzinfo is not None
