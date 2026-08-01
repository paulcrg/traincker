"""Tests pour traincker/reports.py."""

from unittest.mock import patch

from traincker import reports


def test_generer_rapport_texte_sans_donnees(monkeypatch, tmp_path):
    monkeypatch.setattr(
        reports, "charger_donnees", lambda: (_ for _ in ()).throw(FileNotFoundError())
    )
    texte = reports.generer_rapport_texte()
    assert "Aucune donnée" in texte


def test_envoyer_rapport_ignore_si_email_non_configure(monkeypatch):
    monkeypatch.setattr(
        reports, "charger_parametres", lambda: {"canal_email": False, "email_destinataire": ""}
    )
    with patch.object(reports, "send_email_alert") as mock_send:
        resultat = reports.envoyer_rapport_hebdomadaire()
    assert resultat is False
    mock_send.assert_not_called()


def test_envoyer_rapport_envoie_si_configure(monkeypatch):
    monkeypatch.setattr(
        reports,
        "charger_parametres",
        lambda: {"canal_email": True, "email_destinataire": "paul@example.com"},
    )
    monkeypatch.setattr(reports, "generer_rapport_texte", lambda: "Contenu du rapport")

    with patch.object(reports, "send_email_alert") as mock_send:
        resultat = reports.envoyer_rapport_hebdomadaire()

    assert resultat is True
    mock_send.assert_called_once()
    args = mock_send.call_args[0]
    assert args[2] == "paul@example.com"
