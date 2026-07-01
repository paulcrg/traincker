"""Tests unitaires de base pour Traincker."""

from datetime import datetime

from traincker.models import Depart, Trajet, Perturbation


def test_depart_non_perturbe_par_defaut():
    d = Depart(
        ligne="TER",
        direction="Dijon",
        heure_theorique="20260701T080000",
        heure_prevue="20260701T080000",
        statut="base_schedule",
    )
    assert d.est_perturbe is False


def test_depart_perturbe_si_retard_realtime():
    d = Depart(
        ligne="TER",
        direction="Dijon",
        heure_theorique="20260701T080000",
        heure_prevue="20260701T081500",
        statut="realtime",
    )
    assert d.est_perturbe is True


def test_creation_trajet():
    t = Trajet(
        nom="Domicile -> ESEO",
        gare_depart_id="stop_area:SNCF:1",
        gare_depart_nom="Nuits-Saint-Georges",
        gare_arrivee_id="stop_area:SNCF:2",
        gare_arrivee_nom="Dijon Ville",
    )
    assert t.actif is True
    assert "ESEO" in t.nom


def test_creation_perturbation():
    p = Perturbation(titre="Retard", message="Incident technique", severite="delayed")
    assert isinstance(p.date_detection, datetime)
