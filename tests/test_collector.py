"""Tests pour traincker/collector.py."""

import csv

from traincker.collector import historiser_departs


def test_historiser_departs_cree_le_fichier_avec_en_tete(tmp_path):
    csv_path = tmp_path / "departures.csv"
    departs = [
        {
            "ligne": "TER",
            "direction": "Dijon Ville",
            "heure_theorique": "20260701T080000",
            "heure_prevue": "20260701T080000",
            "statut": "base_schedule",
        }
    ]

    historiser_departs(departs, "Nuits-Saint-Georges", path=csv_path)

    assert csv_path.exists()
    with open(csv_path, encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))

    assert len(lignes) == 1
    assert lignes[0]["gare"] == "Nuits-Saint-Georges"
    assert lignes[0]["ligne"] == "TER"


def test_historiser_departs_ajoute_sans_dupliquer_l_en_tete(tmp_path):
    csv_path = tmp_path / "departures.csv"
    depart = [
        {
            "ligne": "TER",
            "direction": "Dijon Ville",
            "heure_theorique": "20260701T080000",
            "heure_prevue": "20260701T081500",
            "statut": "realtime",
        }
    ]

    historiser_departs(depart, "Nuits-Saint-Georges", path=csv_path)
    historiser_departs(depart, "Nuits-Saint-Georges", path=csv_path)

    with open(csv_path, encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))

    assert len(lignes) == 2  # deux lignes de données, un seul en-tête
