"""Tests pour traincker/db.py, avec mock du client Supabase."""

from unittest.mock import MagicMock, patch

from traincker import db


def _reset_singleton():
    """db.py met en cache le client dans des variables de module ; on les remet à zéro entre tests."""
    db._client = None
    db._tentative_faite = False


def test_non_configure_sans_variables_environnement(monkeypatch):
    _reset_singleton()
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    assert db.est_configure() is False


def test_inserer_departs_retourne_false_si_non_configure(monkeypatch):
    _reset_singleton()
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    resultat = db.inserer_departs([{"ligne": "TER", "direction": "X", "heure_theorique": "1", "heure_prevue": "1", "statut": "base_schedule"}], "Gare", "2026-01-01")
    assert resultat is False


def test_charger_departs_retourne_none_si_non_configure(monkeypatch):
    _reset_singleton()
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    assert db.charger_departs() is None


def test_configure_avec_client_mocke(monkeypatch):
    _reset_singleton()
    monkeypatch.setenv("SUPABASE_URL", "https://exemple.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "cle_test")

    faux_client = MagicMock()
    with patch("supabase.create_client", return_value=faux_client):
        assert db.est_configure() is True

        db.inserer_departs(
            [{"ligne": "TER 1", "direction": "Dijon", "heure_theorique": "t", "heure_prevue": "p", "statut": "realtime"}],
            "Nuits-Saint-Georges",
            "2026-01-01T08:00:00",
        )
        faux_client.table.assert_any_call("departures")


def test_alerte_deja_envoyee_none_si_non_configure(monkeypatch):
    _reset_singleton()
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    assert db.alerte_deja_envoyee("cle_test", 3600) is None
