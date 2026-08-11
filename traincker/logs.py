"""
Journal technique, consultable depuis le dashboard sans terminal.

Les horodatages sont stockés directement en heure de Paris (voir
traincker/journal.py pour la même logique côté journal personnel).
"""

from pathlib import Path

from traincker.tz_utils import maintenant_paris

LOG_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "traincker.log"
MAX_LIGNES = 500


def logger(message: str, niveau: str = "INFO") -> None:
    """Ajoute une ligne horodatée au journal, en limitant sa taille."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    horodatage = maintenant_paris().replace(tzinfo=None)
    ligne = f"{horodatage:%Y-%m-%d %H:%M:%S} [{niveau}] {message}\n"

    lignes_existantes = []
    if LOG_PATH.exists():
        with open(LOG_PATH, encoding="utf-8") as f:
            lignes_existantes = f.readlines()

    lignes_existantes.append(ligne)
    lignes_existantes = lignes_existantes[-MAX_LIGNES:]

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.writelines(lignes_existantes)


def lire_logs(nb_lignes: int = 100) -> list[str]:
    """Retourne les dernières lignes du journal, les plus récentes en premier."""
    if not LOG_PATH.exists():
        return []
    with open(LOG_PATH, encoding="utf-8") as f:
        lignes = f.readlines()
    return list(reversed(lignes[-nb_lignes:]))


def vider_logs() -> None:
    if LOG_PATH.exists():
        LOG_PATH.write_text("", encoding="utf-8")
