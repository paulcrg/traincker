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
import pandas as pd

from traincker.api_client import NavitiaClient, NavitiaAPIError
from traincker.favoris import charger_favoris, sauvegarder_favoris
from traincker.models import Trajet
from traincker.utils import formater_heure
from traincker.analysis import (
    charger_donnees,
    stats_ponctualite_par_ligne,
    tendance_retard_dans_le_temps,
    formater_stats_affichage,
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
                    tableau_departs = pd.DataFrame(
                        [
                            {
                                "Ligne": d["ligne"],
                                "Direction": d["direction"],
                                "Départ": formater_heure(d["heure_prevue"]),
                                "Statut": "⏱️ Temps réel"
                                if d["statut"] == "realtime"
                                else "📅 Théorique",
                            }
                            for d in departs
                        ]
                    )
                    st.dataframe(
                        tableau_departs, hide_index=True, use_container_width=True
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
        st.info("Aucun trajet favori configuré pour l'instant. Ajoutes-en un ci-dessous.")
    else:
        for i, trajet in enumerate(favoris):
            col_info, col_toggle, col_delete = st.columns([5, 1, 1])

            with col_info:
                statut_icone = "✅" if trajet.actif else "⏸️"
                st.write(
                    f"{statut_icone} **{trajet.nom}** : "
                    f"{trajet.gare_depart_nom} → {trajet.gare_arrivee_nom}"
                )

            with col_toggle:
                label = "Désactiver" if trajet.actif else "Activer"
                if st.button(label, key=f"toggle_{i}"):
                    favoris[i].actif = not favoris[i].actif
                    sauvegarder_favoris(favoris)
                    st.rerun()

            with col_delete:
                if st.button("🗑️ Suppr.", key=f"delete_{i}"):
                    favoris.pop(i)
                    sauvegarder_favoris(favoris)
                    st.rerun()

    st.divider()
    st.subheader("➕ Ajouter un trajet favori")

    if "recherche_depart" not in st.session_state:
        st.session_state.recherche_depart = []
    if "recherche_arrivee" not in st.session_state:
        st.session_state.recherche_arrivee = []

    nom_trajet = st.text_input(
        "Nom du trajet", placeholder="ex: Domicile -> ESEO", key="nom_trajet_input"
    )

    col_depart, col_arrivee = st.columns(2)

    with col_depart:
        st.write("**Gare de départ**")
        requete_depart = st.text_input(
            "Rechercher une gare", placeholder="ex: Nuits-Saint-Georges", key="requete_depart"
        )
        if st.button("Chercher", key="chercher_depart") and requete_depart:
            try:
                client = NavitiaClient()
                st.session_state.recherche_depart = client.search_station(requete_depart)
                if not st.session_state.recherche_depart:
                    st.warning("Aucune gare trouvée.")
            except NavitiaAPIError as e:
                st.error(f"Erreur API : {e}")

        gare_depart_choisie = None
        if st.session_state.recherche_depart:
            noms = [s["name"] for s in st.session_state.recherche_depart]
            choix = st.selectbox("Résultat", noms, key="choix_depart")
            gare_depart_choisie = next(
                s for s in st.session_state.recherche_depart if s["name"] == choix
            )

    with col_arrivee:
        st.write("**Gare d'arrivée**")
        requete_arrivee = st.text_input(
            "Rechercher une gare", placeholder="ex: Dijon Ville", key="requete_arrivee"
        )
        if st.button("Chercher", key="chercher_arrivee") and requete_arrivee:
            try:
                client = NavitiaClient()
                st.session_state.recherche_arrivee = client.search_station(requete_arrivee)
                if not st.session_state.recherche_arrivee:
                    st.warning("Aucune gare trouvée.")
            except NavitiaAPIError as e:
                st.error(f"Erreur API : {e}")

        gare_arrivee_choisie = None
        if st.session_state.recherche_arrivee:
            noms = [s["name"] for s in st.session_state.recherche_arrivee]
            choix = st.selectbox("Résultat", noms, key="choix_arrivee")
            gare_arrivee_choisie = next(
                s for s in st.session_state.recherche_arrivee if s["name"] == choix
            )

    if st.button("✅ Ajouter ce trajet", type="primary"):
        if not nom_trajet:
            st.warning("Donne un nom au trajet.")
        elif not gare_depart_choisie or not gare_arrivee_choisie:
            st.warning("Cherche et sélectionne une gare de départ ET d'arrivée.")
        else:
            nouveau_trajet = Trajet(
                nom=nom_trajet,
                gare_depart_id=gare_depart_choisie["id"],
                gare_depart_nom=gare_depart_choisie["name"],
                gare_arrivee_id=gare_arrivee_choisie["id"],
                gare_arrivee_nom=gare_arrivee_choisie["name"],
            )
            favoris.append(nouveau_trajet)
            sauvegarder_favoris(favoris)
            st.session_state.recherche_depart = []
            st.session_state.recherche_arrivee = []
            st.success(f"Trajet « {nom_trajet} » ajouté !")
            st.rerun()

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
            st.dataframe(formater_stats_affichage(stats), use_container_width=True)

            st.subheader("Retard moyen par ligne")
            fig_retard = graphe_retard_par_ligne(stats)
            st.pyplot(fig_retard)

            st.subheader("Évolution du retard moyen dans le temps")
            tendance = tendance_retard_dans_le_temps(df)
            fig_tendance = graphe_tendance_temporelle(tendance)
            st.pyplot(fig_tendance)
