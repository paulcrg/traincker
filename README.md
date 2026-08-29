# 🚆 Traincker

![Tests](https://img.shields.io/badge/tests-137%20passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.12-blue)
[![Démo](https://img.shields.io/badge/démo-traincker.app-success)](https://traincker.app)

> Un petit script pour surveiller des trains, devenu un vrai terrain d'apprentissage : Python, données, API, mise en prod.

Suivi personnel des trains SNCF au quotidien : horaires, retards, perturbations,
et alertes automatiques sur les trajets favoris, le tout en Python.

🔗 **[traincker.app](https://traincker.app)** : démo publique (voir la section [Démo publique](#démo-publique) ci-dessous)

## À propos

Tout est parti d'un problème banal : un trajet en train quotidien, et un retard découvert seulement en arrivant sur le quai, faute de notification.

Traincker a d'abord été un simple script pour vérifier les horaires en ligne de commande. Il a ensuite évolué au fil des besoins : des trajets favoris surveillés en continu, des alertes automatiques, puis de l'analyse de données pour comprendre les tendances de ponctualité, et enfin une vraie interface web.

C'est aussi, et surtout, un prétexte pour progresser sérieusement sur :
- la manipulation de données réelles avec `pandas`/`numpy`
- la visualisation avec `matplotlib`
- une interface web réactive (FastAPI + HTMX, sans framework JS)
- une architecture de projet Python propre (séparation des responsabilités, tests, configuration)
- une organisation GitHub soignée (historique de commits clair, README à jour)
- une mise en production réelle (Render, domaine personnalisé, monitoring en continu via GitHub Actions)

Certaines parties du développement (documentation, suggestions de refactoring, aide au debug) se sont appuyées sur des outils d'IA en complément du travail de conception et d'écriture du code. Rien n'y échappe totalement à la relecture et aux tests : la priorité reste donnée à la **fonctionnalité** plutôt qu'à l'esthétique, car c'est un outil utilisé réellement au quotidien, pas une vitrine.

## Fonctionnalités

- 🔎 Recherche des prochains départs pour une gare donnée, avec suggestions en direct
- ⭐ Gestion de trajets favoris (gare départ → gare arrivée)
- 🔔 Alerte Discord/email automatique en cas de perturbation sur un trajet favori
- 📊 Analyse de données (pandas/numpy) : statistiques de ponctualité par ligne/gare
- 📈 Visualisation (matplotlib) : évolution des retards, heatmap jour/heure
- ♿ Accessibilité : contraste élevé, taille de texte, thème clair, appliqués instantanément
- 🖥️ Interface web FastAPI + HTMX (rapide, sans rechargement de page)

## Démo publique

[traincker.app](https://traincker.app) tourne en **mode démo** (`TRAINCKER_DEMO=1`) :
- 7 trajets de démonstration permanents (pour montrer le fonctionnement sans attendre)
- tout trajet ajouté par un visiteur est automatiquement supprimé au bout d'1h

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
| Tests | `pytest` |
| Qualité de code | `black`, `flake8` |
| Déploiement | Render, GitHub Actions (collecte périodique) |

Un dashboard **Streamlit** existe toujours dans `traincker/dashboard.py` (première version du projet, conservée en local à titre historique/comparatif) mais n'est plus déployé en production, voir [Dashboard Streamlit (legacy, optionnel)](#dashboard-streamlit-legacy-optionnel).

## Installation

```bash
git clone https://github.com/paulcrg/traincker.git
cd traincker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# puis remplir .env avec une clé API SNCF et un webhook Discord
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
- `TRAINCKER_DEMO=1` : active le mode démo public (limites, expiration, confidentialité)
- `TRAINCKER_READONLY=1` : verrouille toute modification (lecture seule stricte)

### Dashboard Streamlit (legacy, optionnel)

```bash
pip install streamlit  # pas installé par défaut, retiré de requirements.txt
streamlit run traincker/dashboard.py
```

## Structure du projet

```
traincker/
├── config/                # favoris.json, parametres.json
├── traincker/              # code source du package partagé (API, analyse, CLI...)
│   ├── api_client.py       # wrapper autour de l'API Navitia/SNCF
│   ├── models.py           # dataclasses Trajet, Depart, Perturbation
│   ├── analysis.py         # calculs pandas/numpy (ponctualité, stats)
│   ├── viz.py               # graphes matplotlib
│   ├── monitor.py           # surveillance périodique + alertes
│   ├── db.py                 # persistance Supabase
│   ├── cli.py                 # interface ligne de commande
│   └── dashboard.py           # dashboard Streamlit (legacy, non déployé)
├── traincker_web/            # interface web FastAPI + HTMX (production)
│   ├── main.py                 # routes FastAPI
│   ├── templates/               # templates Jinja2
│   └── static/                   # CSS, logos
├── scripts/                    # scripts ponctuels (ex: génération des trajets démo)
├── data/
│   ├── raw/                     # réponses JSON brutes (historique)
│   └── processed/               # CSV nettoyés pour l'analyse
├── tests/                       # tests unitaires + tests web (pytest)
├── render.yaml                  # config de déploiement Render
└── main.py                      # point d'entrée CLI
```

## Auteur

**Paul Crémoux Guiblain**, étudiant en 2e année du cycle préparatoire intégré à l'ESEO Dijon.

[GitHub](https://github.com/paulcrg)

## Licence

MIT, projet personnel à but pédagogique.
