"""Tests pour traincker/logs.py."""

from traincker import logs


def test_logger_puis_lire_logs(tmp_path, monkeypatch):
    monkeypatch.setattr(logs, "LOG_PATH", tmp_path / "traincker.log")
    logs.logger("Premier message")
    logs.logger("Deuxième message", niveau="ERROR")

    lignes = logs.lire_logs()
    assert len(lignes) == 2
    assert "Deuxième message" in lignes[0]  # le plus récent en premier
    assert "[ERROR]" in lignes[0]


def test_lire_logs_vide_si_fichier_absent(tmp_path, monkeypatch):
    monkeypatch.setattr(logs, "LOG_PATH", tmp_path / "inexistant.log")
    assert logs.lire_logs() == []


def test_logger_limite_le_nombre_de_lignes(tmp_path, monkeypatch):
    monkeypatch.setattr(logs, "LOG_PATH", tmp_path / "traincker.log")
    monkeypatch.setattr(logs, "MAX_LIGNES", 3)
    for i in range(5):
        logs.logger(f"Message {i}")

    lignes = logs.lire_logs(nb_lignes=10)
    assert len(lignes) == 3
    assert "Message 4" in lignes[0]


def test_vider_logs(tmp_path, monkeypatch):
    chemin = tmp_path / "traincker.log"
    monkeypatch.setattr(logs, "LOG_PATH", chemin)
    logs.logger("Un message")
    logs.vider_logs()
    assert logs.lire_logs() == []
