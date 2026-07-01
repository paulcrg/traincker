"""
Analyse de données de ponctualité avec pandas/numpy.

Ce module attend des données historisées dans data/processed/departures.csv
avec au minimum les colonnes : ligne, heure_theorique, heure_prevue, statut.
"""

from pathlib import Path

import numpy as np
import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "departures.csv"


def charger_donnees(path: Path = DATA_PATH) -> pd.DataFrame:
    """Charge le CSV historisé des départs en DataFrame pandas."""
    if not path.exists():
        raise FileNotFoundError(
            f"Aucune donnée historisée trouvée à {path}. "
            "Lance d'abord une collecte via cli.py ou dashboard.py."
        )
    df = pd.read_csv(path, parse_dates=["heure_theorique", "heure_prevue"])
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
