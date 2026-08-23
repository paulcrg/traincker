"""Tests pour traincker_web/main.py (interface FastAPI + HTMX).

Tout est isolé : les fonctions de lecture/écriture de traincker_web.main
sont monkeypatchées pour ne jamais toucher aux vrais fichiers du projet
(config/favoris.json, config/parametres.json, journal, logs).
"""

import csv
import os
from datetime import datetime, timedelta, timezone

import pytest

os.environ.setdefault("SNCF_API_KEY", "dummy_key_pour_tests")

from fastapi.testclient import TestClient

import traincker_web.main as main
from traincker.models import Trajet
from traincker.analysis import charger_donnees as charger_donnees_reel
from traincker.api_client import NavitiaAPIError
from traincker.settings import DEFAUTS as PARAMETRES_DEFAUTS


@pytest.fixture
def client():
    return TestClient(main.app)


@pytest.fixture(autouse=True)
def isoler_kpi(monkeypatch):
    """Les KPI du bandeau supérieur ne doivent jamais dépendre de l'état
    réel du disque pendant les tests."""
    monkeypatch.setattr(
        main,
        "_stats_rapides",
        lambda: {"trajets_actifs": 0, "derniere_collecte": "Aucune", "nb_alertes": 0},
    )


@pytest.fixture(autouse=True)
def invalider_cache_donnees():
    """Le cache TTL de charger_donnees() (et désormais celui des PNG de
    graphiques + celui du bandeau KPI) est un singleton au niveau du
    module : sans ça, un test pourrait récupérer les données/images mises
    en cache par le test précédent au lieu d'appeler son propre mock."""
    main._invalider_cache_donnees()
    main._cache_graphiques.clear()
    main._cache_kpi["valeur"] = None
    main._cache_kpi["expire"] = 0.0
    yield
    main._invalider_cache_donnees()
    main._cache_graphiques.clear()
    main._cache_kpi["valeur"] = None
    main._cache_kpi["expire"] = 0.0


@pytest.fixture
def favoris_memoire(monkeypatch):
    """Remplace charger_favoris/sauvegarder_favoris par une liste en
    mémoire, capturée pour vérification, sans jamais toucher au vrai
    config/favoris.json."""
    etat = {"trajets": []}

    def _charger():
        return list(etat["trajets"])

    def _sauvegarder(trajets):
        etat["trajets"] = list(trajets)

    monkeypatch.setattr(main, "charger_favoris", _charger)
    monkeypatch.setattr(main, "sauvegarder_favoris", _sauvegarder)
    return etat


@pytest.fixture
def parametres_memoire(monkeypatch):
    etat = {"valeurs": PARAMETRES_DEFAUTS.copy()}

    def _charger():
        return dict(etat["valeurs"])

    def _sauvegarder(parametres):
        etat["valeurs"] = dict(parametres)

    monkeypatch.setattr(main, "charger_parametres", _charger)
    monkeypatch.setattr(main, "sauvegarder_parametres", _sauvegarder)
    return etat


@pytest.fixture
def csv_donnees_test(tmp_path):
    """Un petit CSV de départs historisés valide, pour tester les
    statistiques sans dépendre de vraies données collectées."""
    path = tmp_path / "departures.csv"
    lignes_possibles = ["P20", "P21", "TER"]
    gares = ["Dijon Ville", "Nuits-Saint-Georges"]
    rows = []
    base = datetime(2026, 7, 1, 7, 0)
    for jour in range(20):
        for h in (7, 8, 18):
            dt_theorique = base + timedelta(days=jour, hours=h - 7)
            retard = (jour % 6) * 2  # variation deterministe, pas aleatoire
            dt_prevue = dt_theorique + timedelta(minutes=retard)
            rows.append(
                {
                    "horodatage_collecte": dt_theorique.isoformat(),
                    "gare": gares[jour % 2],
                    "ligne": lignes_possibles[jour % 3],
                    "direction": "Dijon",
                    "heure_theorique": dt_theorique.strftime("%Y%m%dT%H%M%S"),
                    "heure_prevue": dt_prevue.strftime("%Y%m%dT%H%M%S"),
                    "statut": "realtime" if retard else "base_schedule",
                }
            )
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "horodatage_collecte", "gare", "ligne", "direction",
                "heure_theorique", "heure_prevue", "statut",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    return path


# --- Pages de base ---------------------------------------------------------

def test_les_quatre_pages_se_chargent(client):
    for url in ["/", "/favoris", "/stats", "/apropos"]:
        r = client.get(url)
        assert r.status_code == 200, url


def test_footer_present_sur_toutes_les_pages(client):
    for url in ["/", "/favoris", "/stats", "/apropos"]:
        assert "tk-footer" in client.get(url).text


def test_nav_actif_correct(client):
    assert 'nav-link active' in client.get("/apropos").text
    r = client.get("/apropos")
    assert '>En savoir plus</a>' in r.text


# --- Recherche ---------------------------------------------------------

def test_suggestions_sous_le_seuil_ne_cherche_pas(client, monkeypatch):
    appelee = {"valeur": False}
    monkeypatch.setattr(main.client, "search_station", lambda q: appelee.__setitem__("valeur", True) or [])
    r = client.get("/gares/suggestions", params={"q": "di"})
    assert r.status_code == 200
    assert appelee["valeur"] is False
    assert "suggestion-vide" not in r.text


def test_suggestions_au_dessus_du_seuil(client, monkeypatch):
    monkeypatch.setattr(
        main.client, "search_station",
        lambda q: [{"id": "stop_area:SNCF:X", "name": "Dijon Ville"}],
    )
    r = client.get("/gares/suggestions", params={"q": "dijon"})
    assert "Dijon Ville" in r.text


def test_departs_succes(client, monkeypatch):
    monkeypatch.setattr(
        main.client, "get_next_departures",
        lambda gare_id, count=5: [{
            "ligne": "P20", "direction": "Dijon",
            "heure_theorique": "20260701T080000",
            "heure_prevue": "20260701T080300", "statut": "realtime",
        }],
    )
    monkeypatch.setattr(main.client, "get_disruptions", lambda gare_id: [])
    r = client.post("/departs", data={"gare_id": "stop_area:SNCF:X", "gare_nom": "Dijon"})
    assert r.status_code == 200
    assert "Dijon" in r.text


def test_departs_erreur_api_affiche_message_sans_planter(client, monkeypatch):
    def _echec(gare_id, count=5):
        raise NavitiaAPIError("panne simulée")
    monkeypatch.setattr(main.client, "get_next_departures", _echec)
    r = client.post("/departs", data={"gare_id": "stop_area:SNCF:X", "gare_nom": "Dijon"})
    assert r.status_code == 200
    assert "panne simulée" in r.text


# --- Favoris ---------------------------------------------------------

def test_favoris_liste_vide(client, favoris_memoire):
    assert "Aucun trajet favori" in client.get("/favoris").text


def test_favoris_ajout(client, favoris_memoire):
    r = client.post("/favoris/ajouter", data={
        "nom": "Test", "gare_depart_id": "A", "gare_depart_nom": "GareA",
        "gare_arrivee_id": "B", "gare_arrivee_nom": "GareB",
    })
    assert r.status_code == 200
    assert "Test" in r.text
    assert len(favoris_memoire["trajets"]) == 1


def test_favoris_toggle(client, favoris_memoire):
    favoris_memoire["trajets"] = [Trajet("T", "A", "GareA", "B", "GareB", actif=True)]
    client.post("/favoris/0/toggle")
    assert favoris_memoire["trajets"][0].actif is False


def test_favoris_suppression(client, favoris_memoire):
    favoris_memoire["trajets"] = [Trajet("T", "A", "GareA", "B", "GareB")]
    r = client.delete("/favoris/0")
    assert r.status_code == 200
    assert len(favoris_memoire["trajets"]) == 0


def test_favoris_creation_trajet_retour(client, favoris_memoire):
    favoris_memoire["trajets"] = [Trajet("Aller", "A", "GareA", "B", "GareB")]
    client.post("/favoris/0/retour")
    assert len(favoris_memoire["trajets"]) == 2
    retour = favoris_memoire["trajets"][1]
    assert retour.gare_depart_id == "B" and retour.gare_arrivee_id == "A"


def test_favoris_pas_de_bouton_retour_si_couple_deja_present(client, favoris_memoire):
    favoris_memoire["trajets"] = [
        Trajet("Aller", "A", "GareA", "B", "GareB"),
        Trajet("Retour", "B", "GareB", "A", "GareA"),
    ]
    r = client.get("/favoris")
    assert r.text.count("Créer le trajet retour") == 0


def test_favoris_appels_api_paralleles(client, favoris_memoire, monkeypatch):
    """Avec plusieurs trajets actifs, les appels API du prochain départ
    doivent partir en parallèle : le temps total doit rester proche de la
    durée d'UN seul appel (~0.2s ici), pas de 5 appels mis bout à bout."""
    import time as _time

    favoris_memoire["trajets"] = [
        Trajet(f"Trajet {i}", f"A{i}", f"GareA{i}", f"B{i}", f"GareB{i}")
        for i in range(5)
    ]

    def _lente(gare_id, count=1):
        _time.sleep(0.2)
        return [{"heure_prevue": "20260701T080000"}]

    monkeypatch.setattr(main.client, "get_next_departures", _lente)

    debut = _time.time()
    r = client.get("/favoris")
    duree = _time.time() - debut

    assert r.status_code == 200
    # 5 appels sequentiels auraient pris ~1s ; en parallele, largement sous 0.6s
    assert duree < 0.6, f"trop lent ({duree:.2f}s) : les appels ne semblent pas parallelises"


def test_favoris_champs_recherche_ont_bien_name_q(client, favoris_memoire):
    """Régression : ces champs n'avaient pas d'attribut name="q", donc
    HTMX n'envoyait jamais le texte tapé au serveur — la recherche de
    gare était silencieusement cassée malgré des tests backend qui
    passaient tous (ils appelaient l'API directement avec q= explicite)."""
    r = client.get("/favoris")
    assert r.text.count('name="q"') == 2

# --- Statistiques ---------------------------------------------------------

def test_stats_page_sans_donnees(client, monkeypatch):
    def _echec():
        raise FileNotFoundError("aucune donnée")
    monkeypatch.setattr(main, "charger_donnees", _echec)
    r = client.get("/stats")
    assert r.status_code == 200
    assert "Pas encore assez" in r.text or "aucune donnée" in r.text.lower()


def test_stats_page_avec_donnees(client, monkeypatch, csv_donnees_test):
    monkeypatch.setattr(main, "charger_donnees", lambda: charger_donnees_reel(path=csv_donnees_test))
    r = client.get("/stats")
    assert r.status_code == 200
    assert "tk-insight" in r.text


def test_stats_graphiques_png(client, monkeypatch, csv_donnees_test):
    monkeypatch.setattr(main, "charger_donnees", lambda: charger_donnees_reel(path=csv_donnees_test))
    for url in ["/stats/graphique/retard-ligne.png", "/stats/graphique/tendance.png", "/stats/graphique/heatmap.png"]:
        r = client.get(url)
        assert r.status_code == 200
        assert r.headers["content-type"] == "image/png"
        assert len(r.content) > 500


def test_stats_export_csv_et_pdf(client, monkeypatch, csv_donnees_test):
    monkeypatch.setattr(main, "charger_donnees", lambda: charger_donnees_reel(path=csv_donnees_test))
    r_csv = client.get("/stats/export/csv")
    assert r_csv.status_code == 200
    assert r_csv.headers["content-type"].startswith("text/csv")

    r_pdf = client.get("/stats/export/pdf")
    assert r_pdf.status_code == 200
    assert r_pdf.headers["content-type"] == "application/pdf"


def test_cache_donnees_evite_les_rechargements_redondants(client, monkeypatch, csv_donnees_test):
    """Une vue de /stats fait jusqu'à 4 appels navigateur (page + 3 PNG) :
    sans cache, ça ferait 4 lectures Supabase/CSV. Avec le cache, une
    seule lecture réelle doit avoir lieu tant que le TTL n'est pas
    écoulé."""
    compteur = {"appels": 0}

    def _charger_et_compter():
        compteur["appels"] += 1
        return charger_donnees_reel(path=csv_donnees_test)

    monkeypatch.setattr(main, "charger_donnees", _charger_et_compter)

    client.get("/stats")
    client.get("/stats/graphique/retard-ligne.png")
    client.get("/stats/graphique/tendance.png")
    client.get("/stats/graphique/heatmap.png")

    assert compteur["appels"] == 1


def test_cache_png_evite_de_regenerer_les_graphiques(client, monkeypatch, csv_donnees_test):
    """Deux visites de /stats/graphique/retard-ligne.png rapprochées ne
    doivent générer le graphique matplotlib qu'une seule fois."""
    monkeypatch.setattr(main, "charger_donnees", lambda: charger_donnees_reel(path=csv_donnees_test))

    compteur = {"appels": 0}
    original = main.graphe_retard_par_ligne

    def _compter(*args, **kwargs):
        compteur["appels"] += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(main, "graphe_retard_par_ligne", _compter)

    client.get("/stats/graphique/retard-ligne.png")
    client.get("/stats/graphique/retard-ligne.png")
    client.get("/stats/graphique/retard-ligne.png")

    assert compteur["appels"] == 1

# --- En savoir plus : export/import config ---------------------------------------------------------

def test_export_config(client, favoris_memoire):
    favoris_memoire["trajets"] = [Trajet("T", "A", "GareA", "B", "GareB")]
    r = client.get("/apropos/export")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/json"
    assert "GareA" in r.text


def test_import_config_valide(client, favoris_memoire):
    contenu = b'{"trajets": [{"nom": "Import", "gare_depart_id": "A", "gare_depart_nom": "GA", "gare_arrivee_id": "B", "gare_arrivee_nom": "GB", "actif": true}]}'
    r = client.post("/apropos/importer", files={"fichier": ("f.json", contenu, "application/json")})
    assert r.status_code == 200
    assert "1 trajet restauré" in r.text
    assert len(favoris_memoire["trajets"]) == 1


def test_import_config_invalide_ne_plante_pas(client, favoris_memoire):
    r = client.post("/apropos/importer", files={"fichier": ("f.json", b"pas du json", "application/json")})
    assert r.status_code == 200
    assert "invalide" in r.text.lower()
    assert len(favoris_memoire["trajets"]) == 0


# --- En savoir plus : paramètres ---------------------------------------------------------

def test_sauvegarde_parametres_alertes(client, parametres_memoire):
    r = client.post("/apropos/parametres/alertes", data={
        "silence_debut": "23:00", "silence_fin": "06:00", "canal_discord": "on",
    })
    assert r.status_code == 200
    assert parametres_memoire["valeurs"]["silence_debut"] == "23:00"
    assert parametres_memoire["valeurs"]["canal_discord"] is True
    assert parametres_memoire["valeurs"]["canal_email"] is False


def test_sauvegarde_parametres_accessibilite_instantanee(client, parametres_memoire):
    r = client.post("/apropos/parametres/accessibilite", data={
        "contraste_eleve": "on", "taille_police": "grande",
    })
    assert r.status_code == 204
    assert parametres_memoire["valeurs"]["contraste_eleve"] is True
    assert parametres_memoire["valeurs"]["taille_police"] == "grande"


def test_bouton_appliquer_absent_du_formulaire_accessibilite(client, parametres_memoire):
    assert ">Appliquer<" not in client.get("/apropos").text


# --- Mode lecture seule ---------------------------------------------------------

def test_lecture_seule_bloque_import_cote_serveur(client, favoris_memoire, monkeypatch):
    monkeypatch.setattr(main, "LECTURE_SEULE", True)
    r = client.post("/apropos/importer", files={"fichier": ("f.json", b'{"trajets":[]}', "application/json")})
    assert "désactivé en lecture seule" in r.text
    r2 = client.post("/apropos/parametres/accessibilite", data={})
    assert r2.status_code == 403


def test_lecture_seule_masque_les_formulaires(client, monkeypatch):
    monkeypatch.setattr(main, "LECTURE_SEULE", True)
    r = client.get("/apropos")
    assert r.text.count("désactivée en lecture seule") == 2


# --- Mode démo ---------------------------------------------------------

def test_demo_limite_le_nombre_de_trajets(client, favoris_memoire, monkeypatch):
    monkeypatch.setattr(main, "MODE_DEMO", True)
    maintenant = datetime.now(timezone.utc).isoformat()
    favoris_memoire["trajets"] = [
        Trajet(f"T{i}", f"A{i}", f"GA{i}", f"B{i}", f"GB{i}", cree_le=maintenant)
        for i in range(5)
    ]
    r = client.post("/favoris/ajouter", data={
        "nom": "Un de trop", "gare_depart_id": "X", "gare_arrivee_id": "Y",
    })
    assert r.status_code == 200
    assert "Limite de 5 trajets ajoutés atteinte" in r.text
    assert len(favoris_memoire["trajets"]) == 5


def test_demo_horodate_les_nouveaux_trajets(client, favoris_memoire, monkeypatch):
    monkeypatch.setattr(main, "MODE_DEMO", True)
    client.post("/favoris/ajouter", data={
        "nom": "Test démo", "gare_depart_id": "A", "gare_arrivee_id": "B",
    })
    assert favoris_memoire["trajets"][0].cree_le is not None


def test_hors_demo_pas_de_limite_ni_horodatage(client, favoris_memoire, monkeypatch):
    monkeypatch.setattr(main, "MODE_DEMO", False)
    favoris_memoire["trajets"] = [
        Trajet(f"T{i}", f"A{i}", f"GA{i}", f"B{i}", f"GB{i}") for i in range(5)
    ]
    r = client.post("/favoris/ajouter", data={
        "nom": "Un de plus", "gare_depart_id": "X", "gare_arrivee_id": "Y",
    })
    assert len(favoris_memoire["trajets"]) == 6
    assert favoris_memoire["trajets"][-1].cree_le is None


def test_demo_expire_les_trajets_de_plus_d_une_heure(client, favoris_memoire, monkeypatch):
    monkeypatch.setattr(main, "MODE_DEMO", True)
    maintenant = datetime.now(timezone.utc)
    favoris_memoire["trajets"] = [
        Trajet("Ancien", "A", "GA", "B", "GB", cree_le=(maintenant - timedelta(hours=2)).isoformat()),
        Trajet("Recent", "C", "GC", "D", "GD", cree_le=(maintenant - timedelta(minutes=10)).isoformat()),
        Trajet("Reel", "E", "GE", "F", "GF"),  # trajet d'origine, sans cree_le -> jamais expire
    ]
    r = client.get("/favoris")
    assert r.status_code == 200
    assert "Ancien" not in r.text
    assert "Recent" in r.text
    assert "Reel" in r.text
    assert len(favoris_memoire["trajets"]) == 2  # la purge a bien ete persistee


def test_demo_bandeau_visible_sur_page_favoris(client, favoris_memoire, monkeypatch):
    monkeypatch.setattr(main, "MODE_DEMO", True)
    assert "Mode démo" in client.get("/favoris").text


def test_hors_demo_pas_de_bandeau(client, favoris_memoire, monkeypatch):
    monkeypatch.setattr(main, "MODE_DEMO", False)
    assert "Mode démo" not in client.get("/favoris").text

# --- Confidentialité en mode démo ---------------------------------------------------------

def test_demo_masque_le_formulaire_alertes_et_email(client, parametres_memoire, monkeypatch):
    monkeypatch.setattr(main, "MODE_DEMO", True)
    parametres_memoire["valeurs"]["email_destinataire"] = "paul.secret@exemple.fr"
    r = client.get("/apropos")
    assert "paul.secret@exemple.fr" not in r.text
    assert "non disponibles sur cette démo" in r.text


def test_demo_bloque_la_sauvegarde_alertes_cote_serveur(client, parametres_memoire, monkeypatch):
    monkeypatch.setattr(main, "MODE_DEMO", True)
    r = client.post("/apropos/parametres/alertes", data={"email_destinataire": "hack@exemple.fr"})
    assert "désactivée" in r.text
    assert parametres_memoire["valeurs"]["email_destinataire"] != "hack@exemple.fr"


def test_demo_les_trajets_permanents_ne_comptent_pas_dans_la_limite(client, favoris_memoire, monkeypatch):
    monkeypatch.setattr(main, "MODE_DEMO", True)
    # 5 trajets permanents (cree_le=None, comme les trajets de demonstration)
    favoris_memoire["trajets"] = [
        Trajet(f"Demo{i}", f"A{i}", f"GA{i}", f"B{i}", f"GB{i}") for i in range(5)
    ]
    r = client.post("/favoris/ajouter", data={
        "nom": "Ajout visiteur", "gare_depart_id": "X", "gare_arrivee_id": "Y",
    })
    assert "Limite" not in r.text
    assert len(favoris_memoire["trajets"]) == 6
    assert favoris_memoire["trajets"][-1].cree_le is not None


# --- Journal et logs ---------------------------------------------------------

def test_vider_journal(client, monkeypatch):
    monkeypatch.setattr(main, "lire_journal", lambda n: [])
    appele = {"valeur": False}
    monkeypatch.setattr(main, "vider_journal", lambda: appele.__setitem__("valeur", True))
    r = client.delete("/apropos/journal")
    assert r.status_code == 200
    assert appele["valeur"] is True


def test_vider_logs(client, monkeypatch):
    monkeypatch.setattr(main, "lire_logs", lambda n: [])
    appele = {"valeur": False}
    monkeypatch.setattr(main, "vider_logs", lambda: appele.__setitem__("valeur", True))
    r = client.delete("/apropos/logs")
    assert r.status_code == 200
    assert appele["valeur"] is True
