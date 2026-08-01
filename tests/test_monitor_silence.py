"""Tests pour la logique de silence dans traincker/monitor.py."""

from datetime import datetime

from traincker.monitor import dans_le_silence


def test_silence_plage_normale():
    parametres = {"silence_debut": "13:00", "silence_fin": "14:00"}
    assert dans_le_silence(parametres, datetime(2026, 1, 1, 13, 30)) is True
    assert dans_le_silence(parametres, datetime(2026, 1, 1, 12, 0)) is False


def test_silence_plage_traversant_minuit():
    parametres = {"silence_debut": "22:00", "silence_fin": "07:00"}
    assert dans_le_silence(parametres, datetime(2026, 1, 1, 23, 0)) is True
    assert dans_le_silence(parametres, datetime(2026, 1, 1, 3, 0)) is True
    assert dans_le_silence(parametres, datetime(2026, 1, 1, 12, 0)) is False
