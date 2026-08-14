"""Tests pour traincker/db.py, avec mock du client Supabase."""

from unittest.mock import MagicMock, patch

from traincker import db


def _reset_singleton():
    db._client = None
    db._tentative_faite = False


def test_non_configure_sans_variables_environnement(monkeypatch):
    _reset_singleton()
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    assert db.est_configure() is False


def test_charger_departs_trie_par_date_decroissante_avec_limite(monkeypatch):
    _reset_singleton()
    monkeypatch.setenv("SUPABASE_URL", "https://exemple.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "cle_test")

    faux_client = MagicMock()
    faux_table = faux_client.table.return_value
    faux_select = faux_table.select.return_value
    faux_order = faux_select.order.return_value
    faux_limit = faux_order.limit.return_value
    faux_limit.execute.return_value = MagicMock(data=[{"horodatage_collecte": "2026-01-02T00:00:00"}])

    with patch("supabase.create_client", return_value=faux_client):
        resultat = db.charger_departs(limite=5000)

    faux_select.order.assert_called_once_with("horodatage_collecte", desc=True)
    faux_order.limit.assert_called_once_with(5000)
    assert resultat == [{"horodatage_collecte": "2026-01-02T00:00:00"}]


def test_charger_dernier_horodatage(monkeypatch):
    _reset_singleton()
    monkeypatch.setenv("SUPABASE_URL", "https://exemple.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "cle_test")

    faux_client = MagicMock()
    faux_limit = faux_client.table.return_value.select.return_value.order.return_value.limit.return_value
    faux_limit.execute.return_value = MagicMock(data=[{"horodatage_collecte": "2026-01-02T10:00:00"}])

    with patch("supabase.create_client", return_value=faux_client):
        resultat = db.charger_dernier_horodatage()

    assert resultat == "2026-01-02T10:00:00"


def test_charger_dernier_horodatage_none_si_non_configure(monkeypatch):
    _reset_singleton()
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    assert db.charger_dernier_horodatage() is None


def test_charger_departs_retourne_none_si_non_configure(monkeypatch):
    _reset_singleton()
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    assert db.charger_departs() is None
