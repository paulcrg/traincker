"""Structures de données utilisées dans tout le projet."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Depart:
    """Représente un train au départ d'une gare."""

    ligne: str
    direction: str
    heure_theorique: Optional[str]
    heure_prevue: Optional[str]
    statut: str  # "base_schedule" (à l'heure) ou "realtime" (temps réel/retard)

    @property
    def est_perturbe(self) -> bool:
        """Un départ est considéré perturbé si l'heure prévue diffère
        de l'heure théorique, ou si le statut l'indique."""
        return (
            self.statut == "realtime"
            and self.heure_theorique != self.heure_prevue
        )


@dataclass
class Trajet:
    """Un trajet favori suivi par l'utilisateur."""

    nom: str
    gare_depart_id: str
    gare_depart_nom: str
    gare_arrivee_id: str
    gare_arrivee_nom: str
    actif: bool = True


@dataclass
class Perturbation:
    """Une perturbation remontée par l'API SNCF."""

    titre: str
    message: str
    severite: Optional[str]
    date_detection: datetime = field(default_factory=datetime.now)
