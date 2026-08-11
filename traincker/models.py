"""Structures de données utilisées dans tout le projet."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Depart:
    ligne: str
    direction: str
    heure_theorique: Optional[str]
    heure_prevue: Optional[str]
    statut: str

    @property
    def est_perturbe(self) -> bool:
        return self.statut == "realtime" and self.heure_theorique != self.heure_prevue


@dataclass
class Trajet:
    nom: str
    gare_depart_id: str
    gare_depart_nom: str
    gare_arrivee_id: str
    gare_arrivee_nom: str
    actif: bool = True


@dataclass
class Perturbation:
    titre: str
    message: str
    severite: Optional[str]
    date_detection: datetime = field(default_factory=datetime.now)
