# 🚆 Traincker

Suivi personnel des trains SNCF au quotidien : horaires, retards, perturbations,
et alertes automatiques sur tes trajets favoris — le tout en Python.

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
python main.py --gare "Dijon"
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
- [ ] Phase 2 — Trajets favoris + détection de perturbation
- [ ] Phase 3 — Alertes Discord automatiques
- [ ] Phase 4 — Historisation des données + stats pandas
- [ ] Phase 5 — Visualisations matplotlib + dashboard Streamlit complet

## Licence

MIT — projet personnel à but pédagogique.
