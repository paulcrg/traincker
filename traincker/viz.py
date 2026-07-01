"""Génération de graphes matplotlib à partir des données de ponctualité."""

import matplotlib.pyplot as plt
import pandas as pd


def graphe_retard_par_ligne(stats: pd.DataFrame, save_path: str = None):
    """Barres du retard moyen par ligne."""
    fig, ax = plt.subplots(figsize=(10, 6))
    stats["retard_moyen"].plot(kind="bar", ax=ax, color="#1f77b4")
    ax.set_ylabel("Retard moyen (minutes)")
    ax.set_xlabel("Ligne")
    ax.set_title("Retard moyen par ligne")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path)
    return fig


def graphe_tendance_temporelle(tendance: pd.Series, save_path: str = None):
    """Courbe de l'évolution du retard moyen dans le temps."""
    fig, ax = plt.subplots(figsize=(10, 5))
    tendance.plot(ax=ax, color="#d62728", marker="o")
    ax.set_ylabel("Retard moyen (minutes)")
    ax.set_xlabel("Date")
    ax.set_title("Évolution du retard moyen dans le temps")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path)
    return fig
