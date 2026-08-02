"""Tests pour traincker/local_cache.py."""

import time

from traincker import local_cache


def test_obtenir_absent_retourne_none(tmp_path, monkeypatch):
    monkeypatch.setattr(local_cache, "CACHE_PATH", tmp_path / "cache.json")
    assert local_cache.obtenir("inexistant") is None


def test_enregistrer_puis_obtenir(tmp_path, monkeypatch):
    monkeypatch.setattr(local_cache, "CACHE_PATH", tmp_path / "cache.json")
    local_cache.enregistrer("gare:dijon", [{"id": "1", "name": "Dijon"}])
    resultat = local_cache.obtenir("gare:dijon")
    assert resultat == [{"id": "1", "name": "Dijon"}]


def test_obtenir_expire_retourne_none(tmp_path, monkeypatch):
    monkeypatch.setattr(local_cache, "CACHE_PATH", tmp_path / "cache.json")
    local_cache.enregistrer("gare:dijon", "valeur")
    resultat = local_cache.obtenir("gare:dijon", duree_validite=-1)
    assert resultat is None


def test_obtenir_meme_expire_renvoie_la_valeur(tmp_path, monkeypatch):
    monkeypatch.setattr(local_cache, "CACHE_PATH", tmp_path / "cache.json")
    local_cache.enregistrer("gare:dijon", "valeur_ancienne")
    resultat = local_cache.obtenir_meme_expire("gare:dijon")
    assert resultat is not None
    valeur, horodatage = resultat
    assert valeur == "valeur_ancienne"
    assert horodatage <= time.time()


def test_obtenir_meme_expire_absent_retourne_none(tmp_path, monkeypatch):
    monkeypatch.setattr(local_cache, "CACHE_PATH", tmp_path / "cache.json")
    assert local_cache.obtenir_meme_expire("inexistant") is None
