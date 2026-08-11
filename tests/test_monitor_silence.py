"""Tests pour la logique de silence dans traincker/monitor.py."""

from datetime import datetime, timezone

from traincker.monitor import dans_le_silence


def test_silence_plage_normale_naif():
    parametres = {"silence_debut": "13:00", "silence_fin": "14:00"}
    assert dans_le_silence(parametres, datetime(2026, 1, 1, 13, 30)) is True
    assert dans_le_silence(parametres, datetime(2026, 1, 1, 12, 0)) is False


def test_silence_plage_traversant_minuit_naif():
    parametres = {"silence_debut": "22:00", "silence_fin": "07:00"}
    assert dans_le_silence(parametres, datetime(2026, 1, 1, 23, 0)) is True
    assert dans_le_silence(parametres, datetime(2026, 1, 1, 3, 0)) is True
    assert dans_le_silence(parametres, datetime(2026, 1, 1, 12, 0)) is False


def test_silence_avec_datetime_utc_aware_convertit_en_paris():
    # 21h30 UTC en été = 23h30 à Paris (UTC+2) -> doit être dans le silence 22h-7h
    parametres = {"silence_debut": "22:00", "silence_fin": "07:00"}
    dt_utc = datetime(2026, 7, 1, 21, 30, tzinfo=timezone.utc)
    assert dans_le_silence(parametres, dt_utc) is True


def test_silence_avec_datetime_utc_hors_silence_avec_conversion():
    # 10h00 UTC en été = 12h00 à Paris -> hors silence 22h-7h
    parametres = {"silence_debut": "22:00", "silence_fin": "07:00"}
    dt_utc = datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc)
    assert dans_le_silence(parametres, dt_utc) is False
