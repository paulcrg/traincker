"""Tests pour traincker/journal.py."""

from traincker import journal


def test_ajouter_et_lire_journal(tmp_path, monkeypatch):
    monkeypatch.setattr(journal, "JOURNAL_PATH", tmp_path / "journal.csv")
    journal.ajouter_entree("recherche", "Dijon")
    journal.ajouter_entree("ajout_favori", "Domicile -> Travail")

    entrees = journal.lire_journal()
    assert len(entrees) == 2
    assert entrees[0]["type"] == "ajout_favori"  # le plus récent en premier
    assert entrees[1]["detail"] == "Dijon"


def test_lire_journal_vide_si_fichier_absent(tmp_path, monkeypatch):
    monkeypatch.setattr(journal, "JOURNAL_PATH", tmp_path / "inexistant.csv")
    assert journal.lire_journal() == []


def test_vider_journal(tmp_path, monkeypatch):
    chemin = tmp_path / "journal.csv"
    monkeypatch.setattr(journal, "JOURNAL_PATH", chemin)
    journal.ajouter_entree("recherche", "Lyon")
    journal.vider_journal()
    assert journal.lire_journal() == []
    assert not chemin.exists()


def test_lire_journal_respecte_la_limite(tmp_path, monkeypatch):
    monkeypatch.setattr(journal, "JOURNAL_PATH", tmp_path / "journal.csv")
    for i in range(10):
        journal.ajouter_entree("recherche", f"Gare {i}")

    entrees = journal.lire_journal(limite=3)
    assert len(entrees) == 3
    assert entrees[0]["detail"] == "Gare 9"
