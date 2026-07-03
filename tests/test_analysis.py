"""Tests pour traincker/analysis.py."""

import csv

import pytest

from traincker.analysis import (
    charger_donnees,
    calculer_retard_minutes,
    stats_ponctualite_par_ligne,
    tendance_retard_dans_le_temps,
)
from traincker.collector import COLONNES


def _ecrire_csv_test(path, lignes):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLONNES)
        writer.writeheader()
        for ligne in lignes:
            writer.writerow(ligne)


@pytest.fixture
def csv_exemple(tmp_path):
    path = tmp_path / "departures.csv"
    _ecrire_csv_test(
        path,
        [
            {
                "horodatage_collecte": "2026-07-01T08:00:00",
                "gare": "Nuits-Saint-Georges",
                "ligne": "TER 1",
                "direction": "Dijon Ville",
                "heure_theorique": "20260701T080000",
                "heure_prevue": "20260701T080000",  # à l'heure
                "statut": "base_schedule",
            },
            {
                "horodatage_collecte": "2026-07-01T08:30:00",
                "gare": "Nuits-Saint-Georges",
                "ligne": "TER 1",
                "direction": "Dijon Ville",
                "heure_theorique": "20260701T083000",
                "heure_prevue": "20260701T084500",  # 15 min de retard
                "statut": "realtime",
            },
            {
                "horodatage_collecte": "2026-07-02T08:00:00",
                "gare": "Nuits-Saint-Georges",
                "ligne": "TER 2",
                "direction": "Dijon Ville",
                "heure_theorique": "20260702T080000",
                "heure_prevue": "20260702T080200",  # 2 min de retard
                "statut": "realtime",
            },
        ],
    )
    return path


def test_charger_donnees_leve_erreur_si_fichier_absent(tmp_path):
    with pytest.raises(FileNotFoundError):
        charger_donnees(path=tmp_path / "inexistant.csv")


def test_charger_donnees_parse_correctement_les_dates(csv_exemple):
    df = charger_donnees(path=csv_exemple)
    assert len(df) == 3
    assert str(df["heure_theorique"].dtype).startswith("datetime64")


def test_calculer_retard_minutes(csv_exemple):
    df = charger_donnees(path=csv_exemple)
    df = calculer_retard_minutes(df)
    retards = sorted(df["retard_minutes"].tolist())
    assert retards == [0.0, 2.0, 15.0]


def test_stats_ponctualite_par_ligne(csv_exemple):
    df = charger_donnees(path=csv_exemple)
    stats = stats_ponctualite_par_ligne(df)

    assert "TER 1" in stats.index
    assert "TER 2" in stats.index
    # TER 1 a un retard moyen de (0 + 15) / 2 = 7.5 min
    assert stats.loc["TER 1", "retard_moyen"] == pytest.approx(7.5)
    # TER 2 n'a qu'un seul train, 2 min de retard
    assert stats.loc["TER 2", "retard_moyen"] == pytest.approx(2.0)


def test_tendance_retard_dans_le_temps(csv_exemple):
    df = charger_donnees(path=csv_exemple)
    tendance = tendance_retard_dans_le_temps(df, freq="D")
    assert len(tendance) == 2  # deux jours distincts (1er et 2 juillet)
