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
    taux de trains à l'heure (retard < 5 min). Trié de la ligne la plus
    fiable à la moins fiable.
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
    return stats.sort_values("taux_ponctualite", ascending=False)


def tendance_retard_dans_le_temps(df: pd.DataFrame, freq: str = "D") -> pd.Series:
    """Retourne le retard moyen agrégé par période (jour par défaut)."""
    df = calculer_retard_minutes(df)
    df = df.set_index("heure_theorique")
    return df["retard_minutes"].resample(freq).mean()


def generer_synthese(stats: pd.DataFrame) -> str:
    """
    Génère une phrase de synthèse lisible à partir des statistiques,
    pour donner un aperçu immédiat sans avoir à lire le tableau.
    """
    if stats.empty:
        return ""

    meilleure = stats["taux_ponctualite"].idxmax()
    pire = stats["taux_ponctualite"].idxmin()
    taux_moyen = stats["taux_ponctualite"].mean()

    if meilleure == pire:
        return (
            f"La ligne {meilleure} affiche {stats.loc[meilleure, 'taux_ponctualite']:.0f} % "
            f"de trains à l'heure en moyenne."
        )

    return (
        f"{meilleure} est la ligne la plus fiable "
        f"({stats.loc[meilleure, 'taux_ponctualite']:.0f} % à l'heure), contre "
        f"{stats.loc[pire, 'taux_ponctualite']:.0f} % pour {pire}. "
        f"Ponctualité moyenne globale : {taux_moyen:.0f} %."
    )


def formater_stats_affichage(stats: pd.DataFrame) -> pd.DataFrame:
    """
    Formate le DataFrame de stats pour l'affichage : unités intégrées
    directement dans les valeurs pour une lecture immédiate, sans avoir
    à se référer aux en-têtes de colonnes. Ne modifie pas les données
    utilisées pour les calculs.
    """
    affichage = pd.DataFrame(index=stats.index)
    affichage["Ponctualité"] = stats["taux_ponctualite"].round(0).astype(int).astype(str) + " %"
    affichage["Retard moyen"] = stats["retard_moyen"].round(1).astype(str) + " min"
    affichage["Régularité"] = "± " + stats["retard_ecart_type"].round(1).astype(str) + " min"
    affichage["Trains observés"] = stats["nb_trains"].astype(int)

    return affichage
