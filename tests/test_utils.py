"""Tests pour traincker/utils.py."""

from datetime import datetime

from traincker.utils import formater_heure


def test_formater_heure_aujourdhui(monkeypatch):
    class FausseDatetime(datetime):
        @classmethod
        def now(cls):
            return datetime(2026, 7, 5, 10, 0, 0)

    import traincker.utils as utils_module

    monkeypatch.setattr(utils_module, "datetime", FausseDatetime)
    assert formater_heure("20260705T144900") == "14:49"


def test_formater_heure_autre_jour(monkeypatch):
    class FausseDatetime(datetime):
        @classmethod
        def now(cls):
            return datetime(2026, 7, 1, 10, 0, 0)

    import traincker.utils as utils_module

    monkeypatch.setattr(utils_module, "datetime", FausseDatetime)
    assert formater_heure("20260705T144900") == "05/07 à 14:49"


def test_formater_heure_vide():
    assert formater_heure("") == "?"
    assert formater_heure(None) == "?"
