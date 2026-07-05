"""
Analyse de données de ponctualité avec pandas/numpy.

Ce module lit les données historisées par traincker/collector.py dans
data/processed/departures.csv.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from traincker.collector import CSV_PATH as DATA_PATH

FORMAT_DATE_NAVITIA = "%Y%m%dT%H%M%S"


def charger_donnees(path: Path = DATA_PATH) -> pd.DataFrame:
    """Charge le CSV historisé des départs en DataFrame pandas."""
    if not path.exists():
        raise FileNotFoundError(
            f"Aucune donnée historisée trouvée à {path}. "
            "Lance d'abord `python main.py surveiller` pour collecter des données."
        )
    df = pd.read_csv(path)
    for col in ["heure_theorique", "heure_prevue"]:
        df[col] = pd.to_datetime(df[col], format=FORMAT_DATE_NAVITIA, errors="coerce")

    # On enlève les lignes où le parsing a échoué (données corrompues/incomplètes)
    df = df.dropna(subset=["heure_theorique", "heure_prevue"])
    return df


def calculer_retard_minutes(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute une colonne 'retard_minutes' calculée à partir des deux heures."""
    df = df.copy()
    df["retard_minutes"] = (
        df["heure_prevue"] - df["heure_theorique"]
    ).dt.total_seconds() / 60
    df["retard_minutes"] = df["retard_minutes"].clip(lower=0)
    return df


def stats_ponctualite_par_ligne(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule, pour chaque ligne, le retard moyen, l'écart-type, et le
    taux de trains à l'heure (retard < 5 min).
    """
    df = calculer_retard_minutes(df)

    stats = df.groupby("ligne")["retard_minutes"].agg(
        retard_moyen="mean",
        retard_ecart_type="std",
        nb_trains="count",
    )
    stats["taux_ponctualite"] = df.groupby("ligne")["retard_minutes"].apply(
        lambda x: np.mean(x < 5) * 100
    )
    return stats.sort_values("retard_moyen", ascending=False)


def tendance_retard_dans_le_temps(df: pd.DataFrame, freq: str = "D") -> pd.Series:
    """Retourne le retard moyen agrégé par période (jour par défaut)."""
    df = calculer_retard_minutes(df)
    df = df.set_index("heure_theorique")
    return df["retard_minutes"].resample(freq).mean()


def formater_stats_affichage(stats: pd.DataFrame) -> pd.DataFrame:
    """
    Formate le DataFrame de stats pour l'affichage (arrondis, noms de
    colonnes lisibles). Ne modifie pas les données utilisées pour les calculs.
    """
    affichage = stats.copy()
    affichage["retard_moyen"] = affichage["retard_moyen"].round(1)
    affichage["retard_ecart_type"] = affichage["retard_ecart_type"].round(1)
    affichage["taux_ponctualite"] = affichage["taux_ponctualite"].round(0).astype(int)

    return affichage.rename(
        columns={
            "retard_moyen": "Retard moyen (min)",
            "retard_ecart_type": "Écart-type (min)",
            "nb_trains": "Nb trains",
            "taux_ponctualite": "Ponctualité (%)",
        }
    )
