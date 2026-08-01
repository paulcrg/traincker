"""Tests pour traincker/analysis.py."""

import csv

import pytest

from traincker.analysis import (
    charger_donnees,
    calculer_retard_minutes,
    stats_ponctualite_par_ligne,
    stats_ponctualite_par_gare,
    tendance_retard_dans_le_temps,
    heatmap_retards_heure_jour,
    detecter_tendance,
    temps_perdu_cumule_minutes,
    formater_stats_affichage,
    generer_synthese,
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
                "heure_prevue": "20260701T080000",
                "statut": "base_schedule",
            },
            {
                "horodatage_collecte": "2026-07-01T08:30:00",
                "gare": "Nuits-Saint-Georges",
                "ligne": "TER 1",
                "direction": "Dijon Ville",
                "heure_theorique": "20260701T083000",
                "heure_prevue": "20260701T084500",
                "statut": "realtime",
            },
            {
                "horodatage_collecte": "2026-07-02T08:00:00",
                "gare": "Dijon Ville",
                "ligne": "TER 2",
                "direction": "Nuits-Saint-Georges",
                "heure_theorique": "20260702T080000",
                "heure_prevue": "20260702T080200",
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
    assert stats.loc["TER 1", "retard_moyen"] == pytest.approx(7.5)
    assert stats.loc["TER 2", "retard_moyen"] == pytest.approx(2.0)


def test_stats_ponctualite_par_gare(csv_exemple):
    df = charger_donnees(path=csv_exemple)
    stats = stats_ponctualite_par_gare(df)
    assert "Nuits-Saint-Georges" in stats.index
    assert "Dijon Ville" in stats.index
    assert stats.loc["Dijon Ville", "nb_trains"] == 1


def test_tendance_retard_dans_le_temps(csv_exemple):
    df = charger_donnees(path=csv_exemple)
    tendance = tendance_retard_dans_le_temps(df, freq="D")
    assert len(tendance) == 2


def test_heatmap_retards_heure_jour(csv_exemple):
    df = charger_donnees(path=csv_exemple)
    pivot = heatmap_retards_heure_jour(df)
    assert 8 in pivot.columns
    assert "Mercredi" in pivot.index  # 01/07/2026 est un mercredi


def test_temps_perdu_cumule_minutes(csv_exemple):
    df = charger_donnees(path=csv_exemple)
    total = temps_perdu_cumule_minutes(df)
    assert total == pytest.approx(17.0)


def test_detecter_tendance_vide_si_pas_assez_de_donnees(csv_exemple):
    df = charger_donnees(path=csv_exemple)
    resultat = detecter_tendance(df, jours_recents=7)
    assert resultat == {}


def test_generer_synthese_identifie_meilleure_et_pire_ligne(csv_exemple):
    df = charger_donnees(path=csv_exemple)
    stats = stats_ponctualite_par_ligne(df)
    synthese = generer_synthese(stats)
    assert "TER 2" in synthese
    assert "TER 1" in synthese
    assert "%" in synthese


def test_generer_synthese_vide_si_stats_vides():
    import pandas as pd
    assert generer_synthese(pd.DataFrame()) == ""


def test_formater_stats_affichage_unites_integrees(csv_exemple):
    df = charger_donnees(path=csv_exemple)
    stats = stats_ponctualite_par_ligne(df)
    affichage = formater_stats_affichage(stats)
    assert "min" in affichage.loc["TER 1", "Retard moyen"]
    assert "%" in affichage.loc["TER 1", "Ponctualité"]
    assert affichage.loc["TER 2", "Trains observés"] == 1
