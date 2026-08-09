"""
Analyse de données de ponctualité avec pandas/numpy.

Lit les données depuis Supabase si configuré (voir traincker/db.py), sinon
depuis le CSV local historisé par traincker/collector.py.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from traincker.collector import CSV_PATH as DATA_PATH
from traincker.db import charger_departs, est_configure

FORMAT_DATE_NAVITIA = "%Y%m%dT%H%M%S"
JOURS_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


def charger_donnees(path: Path = DATA_PATH) -> pd.DataFrame:
    """Charge les départs historisés (Supabase si configuré, sinon CSV local)."""
    if est_configure():
        lignes = charger_departs()
        if not lignes:
            raise FileNotFoundError(
                "Aucune donnée historisée dans Supabase pour l'instant. "
                "Laisse la surveillance GitHub Actions tourner un moment."
            )
        df = pd.DataFrame(lignes)
    else:
        if not path.exists():
            raise FileNotFoundError(
                f"Aucune donnée historisée trouvée à {path}. "
                "Lance d'abord `python main.py surveiller` pour collecter des données."
            )
        df = pd.read_csv(path)

    for col in ["heure_theorique", "heure_prevue"]:
        df[col] = pd.to_datetime(df[col], format=FORMAT_DATE_NAVITIA, errors="coerce")
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
    """Retard moyen, écart-type et taux de ponctualité (retard < 5 min), par ligne."""
    df = calculer_retard_minutes(df)
    stats = df.groupby("ligne")["retard_minutes"].agg(
        retard_moyen="mean", retard_ecart_type="std", nb_trains="count"
    )
    stats["taux_ponctualite"] = df.groupby("ligne")["retard_minutes"].apply(
        lambda x: np.mean(x < 5) * 100
    )
    return stats.sort_values("taux_ponctualite", ascending=False)


def stats_ponctualite_par_gare(df: pd.DataFrame) -> pd.DataFrame:
    """Même chose que par ligne, mais agrégé par gare (score de fiabilité par gare)."""
    df = calculer_retard_minutes(df)
    stats = df.groupby("gare")["retard_minutes"].agg(
        retard_moyen="mean", retard_ecart_type="std", nb_trains="count"
    )
    stats["taux_ponctualite"] = df.groupby("gare")["retard_minutes"].apply(
        lambda x: np.mean(x < 5) * 100
    )
    return stats.sort_values("taux_ponctualite", ascending=False)


def tendance_retard_dans_le_temps(df: pd.DataFrame, freq: str = "D") -> pd.Series:
    """Retourne le retard moyen agrégé par période (jour par défaut)."""
    df = calculer_retard_minutes(df)
    df = df.set_index("heure_theorique")
    return df["retard_minutes"].resample(freq).mean()


def heatmap_retards_heure_jour(df: pd.DataFrame) -> pd.DataFrame:
    """Tableau croisé jour de la semaine x heure de la journée, retard moyen en minutes."""
    df = calculer_retard_minutes(df)
    df = df.copy()
    df["jour"] = df["heure_theorique"].dt.dayofweek.map(lambda i: JOURS_FR[i])
    df["heure"] = df["heure_theorique"].dt.hour
    pivot = df.pivot_table(index="jour", columns="heure", values="retard_minutes", aggfunc="mean")
    return pivot.reindex(JOURS_FR)


def detecter_tendance(df: pd.DataFrame, jours_recents: int = 7) -> dict:
    """Compare le retard moyen récent à la période précédente de même durée."""
    df = calculer_retard_minutes(df)
    df = df.set_index("heure_theorique").sort_index()
    if df.empty:
        return {}

    derniere_date = df.index.max()
    limite_recent = derniere_date - pd.Timedelta(days=jours_recents)
    limite_ancien = limite_recent - pd.Timedelta(days=jours_recents)

    recent = df.loc[limite_recent:derniere_date, "retard_minutes"]
    ancien = df.loc[limite_ancien:limite_recent, "retard_minutes"]

    if recent.empty or ancien.empty:
        return {}

    moyenne_recente = recent.mean()
    moyenne_ancienne = ancien.mean()
    variation = moyenne_recente - moyenne_ancienne

    if abs(variation) < 0.5:
        direction = "stable"
    elif variation > 0:
        direction = "degradation"
    else:
        direction = "amelioration"

    return {
        "direction": direction,
        "variation_minutes": round(variation, 1),
        "moyenne_recente": round(moyenne_recente, 1),
        "moyenne_ancienne": round(moyenne_ancienne, 1),
    }


def temps_perdu_cumule_minutes(df: pd.DataFrame) -> float:
    """Somme totale des minutes de retard observées sur toutes les données historisées."""
    df = calculer_retard_minutes(df)
    return round(df["retard_minutes"].sum(), 1)


def generer_synthese(stats: pd.DataFrame) -> str:
    """Génère une phrase de synthèse lisible à partir des statistiques par ligne."""
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
    """Formate un DataFrame de stats (ligne ou gare) pour l'affichage, unités intégrées."""
    affichage = pd.DataFrame(index=stats.index)
    affichage["Ponctualité"] = stats["taux_ponctualite"].round(0).astype(int).astype(str) + " %"
    affichage["Retard moyen"] = stats["retard_moyen"].round(1).astype(str) + " min"
    affichage["Régularité"] = "± " + stats["retard_ecart_type"].round(1).astype(str) + " min"
    affichage["Trains observés"] = stats["nb_trains"].astype(int)
    return affichage
