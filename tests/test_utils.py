"""Tests pour traincker/utils.py."""

from datetime import datetime

from traincker.utils import formater_heure, calculer_compte_a_rebours


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


def test_compte_a_rebours_dans_le_futur(monkeypatch):
    class FausseDatetime(datetime):
        @classmethod
        def now(cls):
            return datetime(2026, 7, 5, 14, 37, 0)

    import traincker.utils as utils_module

    monkeypatch.setattr(utils_module, "datetime", FausseDatetime)
    assert calculer_compte_a_rebours("20260705T144900") == "12 min"


def test_compte_a_rebours_plus_d_une_heure(monkeypatch):
    class FausseDatetime(datetime):
        @classmethod
        def now(cls):
            return datetime(2026, 7, 5, 13, 5, 0)

    import traincker.utils as utils_module

    monkeypatch.setattr(utils_module, "datetime", FausseDatetime)
    assert calculer_compte_a_rebours("20260705T144900") == "1h44"


def test_compte_a_rebours_train_parti(monkeypatch):
    class FausseDatetime(datetime):
        @classmethod
        def now(cls):
            return datetime(2026, 7, 5, 15, 30, 0)

    import traincker.utils as utils_module

    monkeypatch.setattr(utils_module, "datetime", FausseDatetime)
    assert calculer_compte_a_rebours("20260705T144900") == "Parti"


def test_compte_a_rebours_vide():
    assert calculer_compte_a_rebours("") == "?"
