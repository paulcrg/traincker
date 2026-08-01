"""Tests pour traincker/alerts.py."""

from traincker.alerts import gravite_perturbation, est_critique, format_perturbation_message


def test_gravite_perturbation_connue():
    label, icone = gravite_perturbation("NO_SERVICE")
    assert label == "Critique"


def test_gravite_perturbation_inconnue_par_defaut():
    label, icone = gravite_perturbation("CODE_INEXISTANT")
    assert label == "Mineur"


def test_est_critique():
    assert est_critique("NO_SERVICE") is True
    assert est_critique("REDUCED_SERVICE") is False
    assert est_critique(None) is False


def test_format_perturbation_message_inclut_la_gravite():
    message = format_perturbation_message(
        "Domicile -> Travail",
        [{"titre": "Incident", "message": "Panne signalisation", "severite": "NO_SERVICE"}],
    )
    assert "Critique" in message
    assert "Incident" in message
    assert "Domicile -> Travail" in message
