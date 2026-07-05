"""Génération de graphes matplotlib, adaptés au thème sombre du dashboard."""

import matplotlib.pyplot as plt
import pandas as pd

# Palette alignée avec traincker/theme.py
COULEUR_TEXTE = "#e7ebf1"
COULEUR_GRILLE = "#333d4a"
COULEUR_ACCENT = "#5b8def"
COULEUR_POSITIVE = "#34d1a0"


def _appliquer_style_sombre(fig, ax):
    """Rend fond transparent + texte clair, pour s'intégrer aux cartes de verre."""
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    ax.tick_params(colors=COULEUR_TEXTE)
    ax.xaxis.label.set_color(COULEUR_TEXTE)
    ax.yaxis.label.set_color(COULEUR_TEXTE)
    ax.title.set_color(COULEUR_TEXTE)

    for spine in ax.spines.values():
        spine.set_color(COULEUR_GRILLE)

    ax.grid(color=COULEUR_GRILLE, linewidth=0.6, alpha=0.5)


def graphe_retard_par_ligne(stats: pd.DataFrame, save_path: str = None):
    """Barres du retard moyen par ligne."""
    fig, ax = plt.subplots(figsize=(10, 6))
    stats["retard_moyen"].plot(kind="bar", ax=ax, color=COULEUR_ACCENT)
    ax.set_ylabel("Retard moyen (minutes)")
    ax.set_xlabel("Ligne")
    ax.set_title("Retard moyen par ligne")
    _appliquer_style_sombre(fig, ax)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, transparent=True)
    return fig


def graphe_tendance_temporelle(tendance: pd.Series, save_path: str = None):
    """Courbe de l'évolution du retard moyen dans le temps."""
    fig, ax = plt.subplots(figsize=(10, 5))
    tendance.plot(ax=ax, color=COULEUR_POSITIVE, marker="o")
    ax.set_ylabel("Retard moyen (minutes)")
    ax.set_xlabel("Date")
    ax.set_title("Évolution du retard moyen dans le temps")
    _appliquer_style_sombre(fig, ax)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, transparent=True)
    return fig
