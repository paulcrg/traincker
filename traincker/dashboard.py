"""
Dashboard Streamlit pour Traincker.

Lancer avec :
    streamlit run traincker/dashboard.py
"""

import sys
from pathlib import Path

# Streamlit exécute ce script en ajoutant son propre dossier au sys.path,
# pas la racine du projet : on l'ajoute nous-mêmes pour que
# "import traincker.xxx" fonctionne.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from traincker.api_client import NavitiaClient, NavitiaAPIError
from traincker.favoris import charger_favoris
from traincker.analysis import (
    charger_donnees,
    stats_ponctualite_par_ligne,
    tendance_retard_dans_le_temps,
)
from traincker.viz import graphe_retard_par_ligne, graphe_tendance_temporelle

st.set_page_config(page_title="Traincker", page_icon="🚆", layout="centered")

st.title("🚆 Traincker")
st.caption("Suivi de tes trains au quotidien")

tab_recherche, tab_favoris, tab_stats = st.tabs(
    ["🔎 Recherche", "⭐ Mes trajets favoris", "📊 Statistiques"]
)

with tab_recherche:
    st.subheader("Prochains départs")
    gare_input = st.text_input("Nom de la gare", placeholder="ex: Dijon")

    if gare_input:
        try:
            client = NavitiaClient()
            stations = client.search_station(gare_input)

            if not stations:
                st.warning("Aucune gare trouvée.")
            else:
                station = stations[0]
                st.success(f"Gare sélectionnée : {station['name']}")

                departs = client.get_next_departures(station["id"], count=10)
                if not departs:
                    st.info("Aucun départ dans l'immédiat.")
                else:
                    for d in departs:
                        icone = "⏱️" if d["statut"] == "realtime" else "📅"
                        st.write(
                            f"{icone} **{d['ligne']}** → {d['direction']} "
                            f"à `{d['heure_prevue']}`"
                        )

                disruptions = client.get_disruptions(station["id"])
                if disruptions:
                    st.error("Perturbations en cours :")
                    for p in disruptions:
                        st.write(f"- **{p['titre']}** : {p['message']}")

        except NavitiaAPIError as e:
            st.error(f"Erreur API : {e}")

with tab_favoris:
    st.subheader("Trajets favoris")
    favoris = charger_favoris()

    if not favoris:
        st.info(
            "Aucun trajet favori configuré. "
            "Ajoute-en dans `config/favoris.json`."
        )
    else:
        for trajet in favoris:
            statut_icone = "✅" if trajet.actif else "⏸️"
            st.write(
                f"{statut_icone} **{trajet.nom}** : "
                f"{trajet.gare_depart_nom} → {trajet.gare_arrivee_nom}"
            )

with tab_stats:
    st.subheader("Statistiques de ponctualité")

    try:
        df = charger_donnees()
    except FileNotFoundError:
        st.info(
            "Aucune donnée historisée pour l'instant. Lance "
            "`python main.py surveiller` un moment pour commencer à collecter des données."
        )
    else:
        if df.empty:
            st.info("Pas encore assez de données exploitables pour calculer des stats.")
        else:
            stats = stats_ponctualite_par_ligne(df)
            st.dataframe(stats)

            st.subheader("Retard moyen par ligne")
            fig_retard = graphe_retard_par_ligne(stats)
            st.pyplot(fig_retard)

            st.subheader("Évolution du retard moyen dans le temps")
            tendance = tendance_retard_dans_le_temps(df)
            fig_tendance = graphe_tendance_temporelle(tendance)
            st.pyplot(fig_tendance)
