"""Tests pour traincker/api_client.py."""

from unittest.mock import MagicMock, patch

import pytest

from traincker.api_client import NavitiaClient, NavitiaAPIError


@pytest.fixture
def client():
    return NavitiaClient(api_key="cle_de_test")


def _reponse_mock(json_data: dict, status_code: int = 200):
    reponse = MagicMock()
    reponse.status_code = status_code
    reponse.json.return_value = json_data
    reponse.text = str(json_data)
    return reponse


def test_get_prochain_depart_trajet_appelle_le_bon_endpoint(client):
    """Régression : get_next_departures() renvoie n'importe quel train de
    la gare de départ, sans filtrer par destination — correct sur une
    petite gare à une seule ligne, complètement faux sur un gros hub
    multi-lignes (Paris Nord, Montparnasse...). get_prochain_depart_trajet
    doit utiliser l'endpoint /journeys, qui calcule un vrai trajet entre
    les deux gares précises."""
    with patch.object(client.session, "get") as get_mock:
        get_mock.return_value = _reponse_mock({
            "journeys": [{"departure_date_time": "20260824T203000"}]
        })
        resultat = client.get_prochain_depart_trajet("stop_area:A", "stop_area:B")

    assert resultat == "20260824T203000"
    appel = get_mock.call_args
    assert "/journeys" in appel.args[0]
    assert appel.kwargs["params"]["from"] == "stop_area:A"
    assert appel.kwargs["params"]["to"] == "stop_area:B"


def test_get_prochain_depart_trajet_aucun_resultat(client):
    with patch.object(client.session, "get") as get_mock:
        get_mock.return_value = _reponse_mock({"journeys": []})
        resultat = client.get_prochain_depart_trajet("stop_area:A", "stop_area:B")
    assert resultat is None


def test_get_prochain_depart_trajet_erreur_api(client):
    with patch.object(client.session, "get") as get_mock:
        get_mock.return_value = _reponse_mock({}, status_code=500)
        with pytest.raises(NavitiaAPIError):
            client.get_prochain_depart_trajet("stop_area:A", "stop_area:B")


def test_get_prochain_depart_trajet_deux_destinations_differentes_ne_se_confondent_pas(client):
    """Le symptôme original : deux trajets partant de la même gare mais
    vers des destinations différentes affichaient exactement le même
    horaire. Ce test vérifie que chaque appel passe bien SA PROPRE gare
    d'arrivée à l'API, et non une valeur partagée entre appels."""
    appels_recus = []

    def _get_capture(url, params=None, timeout=None):
        appels_recus.append(dict(params))
        return _reponse_mock({"journeys": [{"departure_date_time": "20260824T203000"}]})

    with patch.object(client.session, "get", side_effect=_get_capture):
        client.get_prochain_depart_trajet("stop_area:PARIS", "stop_area:BRUXELLES")
        client.get_prochain_depart_trajet("stop_area:PARIS", "stop_area:BORDEAUX")

    assert appels_recus[0]["to"] == "stop_area:BRUXELLES"
    assert appels_recus[1]["to"] == "stop_area:BORDEAUX"
    assert appels_recus[0]["to"] != appels_recus[1]["to"]
