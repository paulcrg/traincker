"""Tests pour traincker/weather.py, avec mock des appels réseau."""

from unittest.mock import patch, MagicMock

from traincker.weather import verifier_meteo_defavorable


def _fake_response(json_data):
    mock = MagicMock()
    mock.json.return_value = json_data
    return mock


@patch("traincker.weather.requests.get")
def test_meteo_defavorable_detectee(mock_get):
    mock_get.side_effect = [
        _fake_response({"results": [{"latitude": 47.32, "longitude": 5.04}]}),
        _fake_response({"current": {"weather_code": 95, "temperature_2m": 2.0}}),
    ]

    resultat = verifier_meteo_defavorable("Dijon")
    assert resultat is not None
    assert resultat["condition"] == "Orage"
    assert resultat["temperature"] == 2.0


@patch("traincker.weather.requests.get")
def test_meteo_favorable_retourne_none(mock_get):
    mock_get.side_effect = [
        _fake_response({"results": [{"latitude": 47.32, "longitude": 5.04}]}),
        _fake_response({"current": {"weather_code": 1, "temperature_2m": 18.0}}),
    ]

    resultat = verifier_meteo_defavorable("Dijon")
    assert resultat is None


@patch("traincker.weather.requests.get")
def test_meteo_gare_introuvable_retourne_none(mock_get):
    mock_get.side_effect = [_fake_response({"results": []})]

    resultat = verifier_meteo_defavorable("GareInexistanteXYZ")
    assert resultat is None


@patch("traincker.weather.requests.get")
def test_meteo_erreur_reseau_ne_leve_pas(mock_get):
    import requests
    mock_get.side_effect = requests.exceptions.ConnectionError()

    resultat = verifier_meteo_defavorable("Dijon")
    assert resultat is None
