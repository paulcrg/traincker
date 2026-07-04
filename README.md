# 🚆 Traincker

> Projet personnel — écrit pour apprendre l'analyse de données en Python (pandas/numpy/matplotlib) à travers un cas concret : mes trajets de train du quotidien.

Suivi personnel des trains SNCF au quotidien : horaires, retards, perturbations,
et alertes automatiques sur tes trajets favoris — le tout en Python.

## À propos

Traincker est né d'un besoin très concret : je fais le trajet Nuits-Saint-Georges → Dijon en train tous les jours pour l'école, et je voulais un moyen simple de savoir si mon train est perturbé sans avoir à checker l'appli SNCF à la main.

C'est aussi (et surtout) un prétexte pour progresser sérieusement sur :
- la manipulation de données réelles avec `pandas`/`numpy`
- la visualisation avec `matplotlib`
- une architecture de projet Python propre (séparation des responsabilités, tests, config)
- une organisation GitHub soignée (historique de commits clair, README à jour, roadmap visible)

Priorité donnée à la **fonctionnalité** plutôt qu'à l'esthétique — c'est un outil que j'utilise vraiment, pas une vitrine.

## Fonctionnalités

- 🔎 Recherche des prochains départs pour une gare donnée
- ⭐ Gestion de trajets favoris (gare départ → gare arrivée)
- 🔔 Alerte Discord automatique en cas de perturbation sur un trajet favori
- 📊 Analyse de données (pandas/numpy) : statistiques de ponctualité
- 📈 Visualisation (matplotlib) : évolution des retards dans le temps
- 🖥️ Dashboard Streamlit pour tout visualiser sans taper de commandes

## Stack technique

| Besoin | Outil |
|---|---|
| Appels API | `requests` |
| Secrets | `python-dotenv` |
| Analyse data | `pandas`, `numpy` |
| Visualisation | `matplotlib` |
| Dashboard | `streamlit` |
| Alertes | Webhook Discord |
| Tests | `pytest` |
| Qualité de code | `black`, `flake8` |

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

# Lancer la surveillance en continu des trajets favoris (alertes Discord)
python main.py surveiller --intervalle 5
```

### Dashboard

```bash
streamlit run traincker/dashboard.py
```

## Structure du projet

```
traincker/
├── config/               # favoris.json : trajets suivis par l'utilisateur
├── traincker/            # code source du package
│   ├── api_client.py     # wrapper autour de l'API Navitia/SNCF
│   ├── models.py         # dataclasses Train, Trajet, Perturbation
│   ├── analysis.py       # calculs pandas/numpy (ponctualité, stats)
│   ├── viz.py            # graphes matplotlib
│   ├── alerts.py         # envoi d'alertes via webhook Discord
│   ├── cli.py            # interface ligne de commande
│   └── dashboard.py      # interface Streamlit
├── data/
│   ├── raw/               # réponses JSON brutes (historique)
│   └── processed/         # CSV nettoyés pour l'analyse
├── tests/                 # tests unitaires pytest
└── main.py                # point d'entrée CLI
```

## Roadmap

- [x] Phase 1 — MVP : client API + affichage des prochains départs en CLI
- [x] Phase 2 — Trajets favoris + détection de perturbation + alertes Discord
- [x] Phase 3 — Historisation des données + stats pandas/numpy
- [ ] Phase 4 — Visualisations matplotlib + dashboard Streamlit complet

## Auteur

**Paul Crémoux Guiblain** — étudiant en cycle préparatoire intégré (E1, spécialité Informatique et Électronique) à ESEO Dijon.

[GitHub](https://github.com/paulcrg)

## Licence

MIT — projet personnel à but pédagogique.
