<div align="center">

# 🚆 Traincker

**Suivi personnel des trains SNCF au quotidien** — horaires, retards, perturbations et alertes automatiques sur tes trajets favoris.

[![Tests](https://img.shields.io/badge/tests-137%20passed-brightgreen)](#)
[![Python](https://img.shields.io/badge/python-3.12-blue)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-HTMX-009688)](#)
[![Licence](https://img.shields.io/badge/licence-MIT-lightgrey)](#licence)

**[🔗 traincker.app](https://traincker.app)** — démo publique en ligne

</div>

---

## À propos

Traincker est né d'un besoin très concret : je fais le trajet Nuits-Saint-Georges → Dijon en train tous les jours pour l'école, et je voulais un moyen simple de savoir si mon train est perturbé sans avoir à checker l'appli SNCF à la main.

C'est aussi (et surtout) un prétexte pour progresser sérieusement sur :
- la manipulation de données réelles avec `pandas`/`numpy`
- la visualisation avec `matplotlib`
- une vraie interface web réactive (FastAPI + HTMX, sans framework JS)
- une architecture de projet Python propre (séparation des responsabilités, tests, config)
- une organisation GitHub soignée (historique de commits clair, README à jour, roadmap visible)
- une mise en production réelle (Render, domaine personnalisé, monitoring en continu via GitHub Actions)

Priorité donnée à la **fonctionnalité** plutôt qu'à l'esthétique — c'est un outil que j'utilise vraiment, pas une vitrine.

## Fonctionnalités

| | |
|---|---|
| 🔎 **Recherche instantanée** | Prochains départs pour une gare donnée, suggestions en direct |
| ⭐ **Trajets favoris** | Gare départ → gare arrivée, prochain train filtré par destination |
| 🔔 **Alertes automatiques** | Discord/email en cas de perturbation sur un trajet favori |
| 📊 **Analyse de données** | Statistiques de ponctualité par ligne/gare (pandas/numpy) |
| 📈 **Visualisations** | Évolution des retards, heatmap jour/heure (matplotlib) |
| ♿ **Accessibilité** | Contraste élevé, taille de texte, thème clair — instantanés |
| 🖥️ **Interface réactive** | FastAPI + HTMX, aucun rechargement de page |

## Démo publique

[traincker.app](https://traincker.app) tourne en **mode démo** (`TRAINCKER_DEMO=1`) :
- 5 trajets de démonstration permanents (pour montrer le fonctionnement sans attendre)
- tout trajet ajouté par un visiteur est automatiquement supprimé au bout d'1h
- les réglages personnels (email, alertes Discord) du propriétaire du projet restent privés, jamais exposés publiquement

## Stack technique

| Besoin | Outil |
|---|---|
| Appels API | `requests` |
| Secrets | `python-dotenv` |
| Analyse data | `pandas`, `numpy` |
| Visualisation | `matplotlib` |
| Interface web | `FastAPI` + `HTMX` + `Jinja2` |
| Base de données | `Supabase` (Postgres) |
| Alertes | Webhook Discord, email |
| Tests | `pytest` (137 tests) |
| Qualité de code | `black`, `flake8` |
| Déploiement | Render, GitHub Actions (collecte + surveillance périodiques) |

Un dashboard **Streamlit** existe toujours dans `traincker/dashboard.py` (première version du projet, conservée en local à titre historique/comparatif) mais n'est plus déployé en production — voir [Dashboard Streamlit (legacy, optionnel)](#dashboard-streamlit-legacy-optionnel).

## Installation

```bash
git clone https://github.com/paulcrg/traincker.git
cd traincker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# puis remplis .env avec ta clé API SNCF et ton webhook Discord
```

## Utilisation

### CLI

```bash
# Prochains départs d'une gare
python main.py gare --gare "Dijon"

# Perturbations en cours sur une gare
python main.py perturbations --gare "Dijon"

# Trouver l'identifiant (stop_area_id) d'une gare, pour remplir config/favoris.json
python main.py recherche --gare "Nuits-Saint-Georges"

# Lancer la surveillance en continu des trajets favoris (alertes Discord/email)
python main.py surveiller --intervalle 5
```

### Interface web (FastAPI + HTMX)

```bash
uvicorn traincker_web.main:app --reload
```

Puis direction `http://127.0.0.1:8000`.

Variables d'environnement optionnelles :
- `TRAINCKER_DEMO=1` — active le mode démo public (limites, expiration, confidentialité)
- `TRAINCKER_READONLY=1` — verrouille toute modification (lecture seule stricte)

### Dashboard Streamlit (legacy, optionnel)

```bash
pip install streamlit  # pas installé par défaut, retiré de requirements.txt
streamlit run traincker/dashboard.py
```

### Tests

```bash
pip install pytest
python -m pytest tests/ -q
```

## Structure du projet

```
traincker/
├── config/                 # favoris.json, parametres.json
├── traincker/               # code source du package partagé (API, analyse, CLI...)
│   ├── api_client.py        # wrapper autour de l'API Navitia/SNCF
│   ├── models.py            # dataclasses Trajet, Depart, Perturbation
│   ├── analysis.py          # calculs pandas/numpy (ponctualité, stats)
│   ├── viz.py                # graphes matplotlib
│   ├── monitor.py            # surveillance périodique + alertes
│   ├── db.py                  # persistance Supabase
│   ├── cli.py                  # interface ligne de commande
│   └── dashboard.py            # dashboard Streamlit (legacy, non déployé)
├── traincker_web/             # interface web FastAPI + HTMX (production)
│   ├── main.py                  # routes FastAPI
│   ├── templates/                # templates Jinja2
│   └── static/                    # CSS, logos
├── scripts/                     # scripts ponctuels (ex: génération des trajets démo)
├── data/
│   ├── raw/                      # réponses JSON brutes (historique)
│   └── processed/                # CSV nettoyés pour l'analyse
├── tests/                        # tests unitaires + tests web (pytest)
├── .github/workflows/            # collecte + surveillance périodiques (GitHub Actions)
├── render.yaml                   # config de déploiement Render
└── main.py                       # point d'entrée CLI
```

## Roadmap

- [x] Phase 1 — MVP : client API + affichage des prochains départs en CLI
- [x] Phase 2 — Trajets favoris + détection de perturbation + alertes Discord
- [x] Phase 3 — Historisation des données + stats pandas/numpy
- [x] Phase 4 — Visualisations matplotlib + dashboard Streamlit complet
- [x] Phase 5 — Migration vers une interface web FastAPI + HTMX, déploiement en mode démo public sur traincker.app
- [ ] Phase 6 — Traduction multilingue de l'interface FastAPI

## Auteur

**Paul Crémoux Guiblain** — étudiant en cycle préparatoire intégré (2ᵉ année, spécialité Informatique et Électronique) à ESEO Dijon.

[GitHub](https://github.com/paulcrg)

## Licence

MIT — projet personnel à but pédagogique.
