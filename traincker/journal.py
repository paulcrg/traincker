"""
Journal personnel : trace les recherches et trajets consultés au fil du
temps. Les horodatages sont stockés directement en heure de Paris (plutôt
que l'heure du serveur, UTC sur GitHub Actions/Render) pour être corrects
à l'affichage sans conversion supplémentaire.
"""

import csv
from pathlib import Path

from traincker.tz_utils import maintenant_paris

JOURNAL_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "journal.csv"
COLONNES = ["horodatage", "type", "detail"]


def ajouter_entree(type_evenement: str, detail: str) -> None:
    """Ajoute une entrée au journal (ex: type='recherche', detail='Dijon')."""
    JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    fichier_existe = JOURNAL_PATH.exists()

    with open(JOURNAL_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLONNES)
        if not fichier_existe:
            writer.writeheader()
        writer.writerow(
            {
                "horodatage": maintenant_paris().replace(tzinfo=None).isoformat(),
                "type": type_evenement,
                "detail": detail,
            }
        )


def lire_journal(limite: int = 50) -> list[dict]:
    """Retourne les dernières entrées du journal, les plus récentes en premier."""
    if not JOURNAL_PATH.exists():
        return []
    with open(JOURNAL_PATH, encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    return list(reversed(lignes[-limite:]))


def vider_journal() -> None:
    if JOURNAL_PATH.exists():
        JOURNAL_PATH.unlink()
