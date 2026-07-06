"""
Dashboard Streamlit pour Traincker.

Lancer avec :
    streamlit run traincker/dashboard.py
"""

import sys
import base64
import json
import csv
import io
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from traincker.api_client import NavitiaClient, NavitiaAPIError
from traincker.favoris import charger_favoris, sauvegarder_favoris
from traincker.models import Trajet
from traincker.utils import formater_heure, calculer_compte_a_rebours
from traincker.analysis import (
    charger_donnees,
    stats_ponctualite_par_ligne,
    tendance_retard_dans_le_temps,
    formater_stats_affichage,
    generer_synthese,
)
from traincker.viz import graphe_retard_par_ligne, graphe_tendance_temporelle
from traincker.theme import THEME_CSS, TAB_SLIDER_JS
from traincker.icons import icono, titre_section
from traincker.monitor import ETAT_PATH
from traincker.collector import CSV_PATH

_logo_path = Path(__file__).resolve().parent.parent / "assets" / "logo-white.png"

st.set_page_config(
    page_title="Traincker",
    page_icon=str(_logo_path) if _logo_path.exists() else None,
    layout="centered",
)
st.markdown(THEME_CSS, unsafe_allow_html=True)


# --- Appels API mis en cache (évite de spammer l'API à chaque rerun Streamlit) ---

@st.cache_data(ttl=120, show_spinner=False)
def rechercher_gares_cache(query: str):
    client = NavitiaClient()
    return client.search_station(query)


@st.cache_data(ttl=20, show_spinner=False)
def obtenir_departs_et_perturbations_gare(station_id: str):
    client = NavitiaClient()
    departs = client.get_next_departures(station_id, count=10)
    perturbations = client.get_disruptions(station_id)
    return departs, perturbations


@st.cache_data(ttl=30, show_spinner=False)
def obtenir_next_depart_et_perturbations(gare_depart_id: str, gare_arrivee_id: str):
    client = NavitiaClient()
    departs = client.get_next_departures(gare_depart_id, count=1)
    perturbations = client.get_disruptions(gare_depart_id)
    perturbations += client.get_disruptions(gare_arrivee_id)
    depart = departs[0] if departs else None
    return depart, perturbations


def obtenir_infos_favoris(favoris: list) -> list:
    """Prochain départ + perturbations pour chaque trajet favori actif."""
    infos = []
    for trajet in favoris:
        info = {"trajet": trajet, "prochain_depart": None, "perturbations": []}
        if trajet.actif:
            try:
                depart, perturbations = obtenir_next_depart_et_perturbations(
                    trajet.gare_depart_id, trajet.gare_arrivee_id
                )
                info["prochain_depart"] = depart
                info["perturbations"] = perturbations
            except NavitiaAPIError:
                pass
        infos.append(info)
    return infos


def bloc_suggestions(stations: list, cle: str):
    """
    Affiche une liste de suggestions cliquables façon dropdown de moteur de
    recherche. Retourne la station cliquée, ou None si aucun clic ce tour-ci.
    """
    resultat = None
    with st.container(key=f"suggest_box_{cle}"):
        for s in stations:
            if st.button(s["name"], key=f"sugg_{cle}_{s['id']}", use_container_width=True):
                resultat = s
    return resultat


# --- Logo + titre ---

if _logo_path.exists():
    _logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode()
    st.markdown(
        f'<div class="tk-logo-wrap">'
        f'<img src="data:image/png;base64,{_logo_b64}" alt="Traincker" style="height:46px;">'
        f"</div>",
        unsafe_allow_html=True,
    )
else:
    st.title("Traincker")

st.markdown(
    '<p class="tk-caption">Suivi de trains au quotidien</p>',
    unsafe_allow_html=True,
)


# --- Chips de statistiques rapides ---

def obtenir_stats_rapides() -> dict:
    favoris = charger_favoris()
    nb_actifs = sum(1 for t in favoris if t.actif)

    derniere_collecte = "Aucune"
    if CSV_PATH.exists():
        try:
            with open(CSV_PATH, encoding="utf-8") as f:
                lignes = list(csv.DictReader(f))
            if lignes:
                dt = datetime.fromisoformat(lignes[-1]["horodatage_collecte"])
                derniere_collecte = dt.strftime("%d/%m %H:%M")
        except (KeyError, ValueError, IndexError):
            pass

    nb_alertes = 0
    if ETAT_PATH.exists():
        try:
            with open(ETAT_PATH, encoding="utf-8") as f:
                nb_alertes = len(json.load(f))
        except (json.JSONDecodeError, OSError):
            pass

    return {
        "trajets_actifs": nb_actifs,
        "derniere_collecte": derniere_collecte,
        "nb_alertes": nb_alertes,
    }


_stats_rapides = obtenir_stats_rapides()
st.markdown(
    f"""
    <div class="tk-chip-row">
        <div class="tk-chip">
            <span class="tk-chip-label">Trajets actifs</span>
            <span class="tk-chip-value">{_stats_rapides['trajets_actifs']}</span>
        </div>
        <div class="tk-chip">
            <span class="tk-chip-label">Dernière collecte</span>
            <span class="tk-chip-value">{_stats_rapides['derniere_collecte']}</span>
        </div>
        <div class="tk-chip">
            <span class="tk-chip-label">Alertes envoyées</span>
            <span class="tk-chip-value">{_stats_rapides['nb_alertes']}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# --- Bandeau global de perturbation active ---

_favoris_globaux = charger_favoris()
_infos_favoris = obtenir_infos_favoris(_favoris_globaux)
_favoris_perturbes = [info for info in _infos_favoris if info["perturbations"]]

if _favoris_perturbes:
    _lignes_banniere = "<br>".join(
        f'<span class="tk-dot tk-dot-alert"></span><strong>{info["trajet"].nom}</strong> : '
        f'{info["perturbations"][0]["titre"]}'
        for info in _favoris_perturbes
    )
    st.markdown(
        f'<div class="tk-banner-alert">{icono("alert", size=18)} '
        f"Perturbation en cours sur un trajet favori<br>{_lignes_banniere}</div>",
        unsafe_allow_html=True,
    )


tab_recherche, tab_favoris, tab_stats = st.tabs(
    ["Recherche", "Mes trajets favoris", "Statistiques"]
)
st.markdown(TAB_SLIDER_JS, unsafe_allow_html=True)

with tab_recherche:
    with st.container(border=True, key="card_recherche"):
        st.markdown(titre_section("search", "Prochains départs"), unsafe_allow_html=True)
        st.markdown(
            '<p class="tk-hint">Tape le nom d\'une gare (3 caractères minimum) '
            "pour voir ses prochains départs.</p>",
            unsafe_allow_html=True,
        )

        if "historique_recherches" not in st.session_state:
            st.session_state.historique_recherches = []
        if "station_recherche" not in st.session_state:
            st.session_state.station_recherche = None

        # On applique la valeur "en attente" AVANT de créer le widget
        # (Streamlit interdit de modifier st.session_state["gare_input"]
        # après que ce widget ait été instancié dans le même run)
        if "gare_input_pendiente" in st.session_state:
            st.session_state["gare_input"] = st.session_state.pop("gare_input_pendiente")

        col_input, col_refresh = st.columns([5, 1])
        with col_input:
            gare_input = st.text_input(
                "Nom de la gare",
                placeholder="ex: Dijon (min. 3 caractères)",
                key="gare_input",
                label_visibility="collapsed",
            )
        with col_refresh:
            if st.button("Rafraîchir", key="refresh_recherche", use_container_width=True):
                rechercher_gares_cache.clear()
                obtenir_departs_et_perturbations_gare.clear()
                st.rerun()

        if st.session_state.historique_recherches:
            st.markdown('<p class="tk-history-label">Recherches récentes</p>', unsafe_allow_html=True)
            cols_historique = st.columns(len(st.session_state.historique_recherches))
            for col, item in zip(cols_historique, st.session_state.historique_recherches):
                with col:
                    if st.button(item["name"], key=f"hist_{item['id']}", use_container_width=True):
                        st.session_state.station_recherche = item
                        st.session_state["gare_input_pendiente"] = item["name"]
                        st.rerun()

        station = st.session_state.station_recherche

        if gare_input and len(gare_input.strip()) >= 3:
            # Si le champ ne correspond plus à la station déjà choisie, on ré-affiche les suggestions
            if not station or station["name"] != gare_input:
                try:
                    stations = rechercher_gares_cache(gare_input)
                except NavitiaAPIError as e:
                    st.error(f"Erreur API : {e}")
                    stations = []

                if not stations:
                    st.warning("Aucune gare trouvée.")
                    station = None
                else:
                    clique = bloc_suggestions(stations, cle="recherche")
                    if clique:
                        st.session_state.station_recherche = clique
                        st.session_state["gare_input_pendiente"] = clique["name"]
                        st.rerun()
                    station = None
        else:
            station = None
            if gare_input:
                st.caption("Continue à taper (3 caractères minimum)...")

        if station:
            try:
                departs, disruptions = obtenir_departs_et_perturbations_gare(station["id"])

                if not departs:
                    st.info("Aucun départ dans l'immédiat.")
                else:
                    tableau_departs = pd.DataFrame(
                        [
                            {
                                "Ligne": d["ligne"],
                                "Direction": d["direction"],
                                "Départ": formater_heure(d["heure_prevue"]),
                                "Statut": "Temps réel" if d["statut"] == "realtime" else "Théorique",
                            }
                            for d in departs
                        ]
                    )
                    st.dataframe(tableau_departs, hide_index=True, use_container_width=True)

                if disruptions:
                    st.markdown(
                        f'<p class="tk-status-line"><span class="tk-dot tk-dot-alert"></span>'
                        f"Perturbations en cours</p>",
                        unsafe_allow_html=True,
                    )
                    for p in disruptions:
                        st.write(f"- **{p['titre']}** : {p['message']}")
                else:
                    st.markdown(
                        '<p class="tk-status-line"><span class="tk-dot tk-dot-ok"></span>'
                        "Aucune perturbation signalée</p>",
                        unsafe_allow_html=True,
                    )

                hist = st.session_state.historique_recherches
                hist = [h for h in hist if h["id"] != station["id"]]
                hist.insert(0, station)
                st.session_state.historique_recherches = hist[:5]

            except NavitiaAPIError as e:
                st.error(f"Erreur API : {e}")

with tab_favoris:
    with st.container(border=True, key="card_favoris_liste"):
        st.markdown(titre_section("star", "Trajets favoris"), unsafe_allow_html=True)

        if not _infos_favoris:
            st.info("Aucun trajet favori configuré pour l'instant. Ajoutes-en un ci-dessous.")
        else:
            for i, info in enumerate(_infos_favoris):
                trajet = info["trajet"]
                col_dot, col_info, col_toggle, col_delete = st.columns(
                    [0.35, 4.15, 1.25, 1.25], gap="small"
                )

                with col_dot:
                    dot_class = "tk-dot-ok" if trajet.actif else "tk-dot-alert"
                    st.markdown(
                        f'<span class="tk-dot {dot_class}" style="margin-top:14px;"></span>',
                        unsafe_allow_html=True,
                    )

                with col_info:
                    st.write(f"**{trajet.nom}** : {trajet.gare_depart_nom} → {trajet.gare_arrivee_nom}")
                    if trajet.actif and info["prochain_depart"]:
                        depart = info["prochain_depart"]
                        heure = formater_heure(depart["heure_prevue"])
                        countdown = calculer_compte_a_rebours(depart["heure_prevue"])
                        st.markdown(
                            f'<div class="tk-next-train">'
                            f'<span class="tk-next-train-time">{heure}</span>'
                            f'<span class="tk-next-train-countdown">{countdown}</span>'
                            f"</div>",
                            unsafe_allow_html=True,
                        )

                with col_toggle:
                    st.markdown('<div class="tk-compact-btn">', unsafe_allow_html=True)
                    label_toggle = "Désactiver" if trajet.actif else "Activer"
                    if st.button(label_toggle, key=f"toggle_{i}", use_container_width=True):
                        favoris_maj = charger_favoris()
                        favoris_maj[i].actif = not favoris_maj[i].actif
                        sauvegarder_favoris(favoris_maj)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                with col_delete:
                    st.markdown('<div class="tk-compact-btn">', unsafe_allow_html=True)
                    if st.button("Supprimer", key=f"delete_{i}", use_container_width=True):
                        st.session_state[f"confirm_delete_{i}"] = True
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                if st.session_state.get(f"confirm_delete_{i}"):
                    st.markdown(
                        f'<p class="tk-confirm-text">Supprimer « {trajet.nom} » ? '
                        f"Cette action est irréversible.</p>",
                        unsafe_allow_html=True,
                    )
                    col_confirm, col_annuler, _ = st.columns([1, 1, 3])
                    with col_confirm:
                        if st.button("Confirmer", key=f"confirm_yes_{i}", use_container_width=True):
                            favoris_maj = charger_favoris()
                            favoris_maj.pop(i)
                            sauvegarder_favoris(favoris_maj)
                            st.session_state[f"confirm_delete_{i}"] = False
                            st.rerun()
                    with col_annuler:
                        if st.button("Annuler", key=f"confirm_no_{i}", use_container_width=True):
                            st.session_state[f"confirm_delete_{i}"] = False
                            st.rerun()

                if i < len(_infos_favoris) - 1:
                    st.markdown('<div class="tk-divider"></div>', unsafe_allow_html=True)

    with st.container(border=True, key="card_favoris_ajout"):
        st.markdown(titre_section("plus", "Ajouter un trajet favori"), unsafe_allow_html=True)
        st.markdown(
            '<p class="tk-hint">Cherche une gare de départ et d\'arrivée, '
            "clique sur une suggestion, puis valide.</p>",
            unsafe_allow_html=True,
        )

        nom_trajet = st.text_input(
            "Nom du trajet", placeholder="ex: Domicile -> ESEO", key="nom_trajet_input"
        )

        for cle_gare, label_gare, placeholder_gare in [
            ("depart", "Gare de départ", "ex: Nuits-Saint-Georges"),
            ("arrivee", "Gare d'arrivée", "ex: Dijon Ville"),
        ]:
            st.write(f"**{label_gare}**")
            requete = st.text_input(
                "Rechercher (3 car. min.)", placeholder=placeholder_gare, key=f"requete_{cle_gare}",
                label_visibility="collapsed",
            )
            session_key = f"station_{cle_gare}"
            if session_key not in st.session_state:
                st.session_state[session_key] = None

            station_gare = st.session_state[session_key]

            if requete and len(requete.strip()) >= 3:
                if not station_gare or station_gare["name"] != requete:
                    try:
                        resultats = rechercher_gares_cache(requete)
                    except NavitiaAPIError as e:
                        st.error(f"Erreur API : {e}")
                        resultats = []

                    if not resultats:
                        st.warning("Aucune gare trouvée.")
                    else:
                        clique = bloc_suggestions(resultats, cle=cle_gare)
                        if clique:
                            st.session_state[session_key] = clique
                            st.rerun()
            else:
                st.session_state[session_key] = None

        gare_depart_choisie = st.session_state.get("station_depart")
        gare_arrivee_choisie = st.session_state.get("station_arrivee")

        if gare_depart_choisie:
            st.caption(f"Départ sélectionné : {gare_depart_choisie['name']}")
        if gare_arrivee_choisie:
            st.caption(f"Arrivée sélectionnée : {gare_arrivee_choisie['name']}")

        if st.button("Ajouter ce trajet", type="primary"):
            if not nom_trajet:
                st.warning("Donne un nom au trajet.")
            elif not gare_depart_choisie or not gare_arrivee_choisie:
                st.warning("Cherche et sélectionne une gare de départ ET d'arrivée.")
            else:
                favoris_maj = charger_favoris()
                favoris_maj.append(
                    Trajet(
                        nom=nom_trajet,
                        gare_depart_id=gare_depart_choisie["id"],
                        gare_depart_nom=gare_depart_choisie["name"],
                        gare_arrivee_id=gare_arrivee_choisie["id"],
                        gare_arrivee_nom=gare_arrivee_choisie["name"],
                    )
                )
                sauvegarder_favoris(favoris_maj)
                st.session_state["station_depart"] = None
                st.session_state["station_arrivee"] = None
                st.success(f"Trajet « {nom_trajet} » ajouté !")
                st.rerun()

with tab_stats:
    with st.container(border=True, key="card_stats"):
        st.markdown(titre_section("chart", "Statistiques de ponctualité"), unsafe_allow_html=True)

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
                stats_affichage = formater_stats_affichage(stats)

                synthese = generer_synthese(stats)
                if synthese:
                    st.markdown(f'<div class="tk-insight">{synthese}</div>', unsafe_allow_html=True)

                st.dataframe(
                    stats_affichage,
                    use_container_width=True,
                    column_config={
                        "Ponctualité": st.column_config.TextColumn(help="Part des trains partis avec moins de 5 min de retard"),
                        "Retard moyen": st.column_config.TextColumn(help="Retard moyen constaté sur la ligne"),
                        "Régularité": st.column_config.TextColumn(help="Écart-type du retard : plus c'est bas, plus la ligne est régulière"),
                        "Trains observés": st.column_config.NumberColumn(help="Nombre de départs historisés pour cette ligne"),
                    },
                )
                st.markdown(
                    '<p class="tk-legend">Un train est considéré « à l\'heure » '
                    "s'il part avec moins de 5 minutes de retard.</p>",
                    unsafe_allow_html=True,
                )

                st.subheader("Retard moyen par ligne")
                fig_retard = graphe_retard_par_ligne(stats)
                st.pyplot(fig_retard)

                st.subheader("Évolution du retard moyen dans le temps")
                tendance = tendance_retard_dans_le_temps(df)
                fig_tendance = graphe_tendance_temporelle(tendance)
                st.pyplot(fig_tendance)

                st.divider()
                st.markdown(titre_section("download", "Exporter"), unsafe_allow_html=True)
                col_csv, col_pdf = st.columns(2)

                with col_csv:
                    csv_bytes = stats_affichage.to_csv().encode("utf-8")
                    st.download_button(
                        "Export CSV",
                        data=csv_bytes,
                        file_name="traincker_stats.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )

                with col_pdf:
                    buffer_pdf = io.BytesIO()
                    with PdfPages(buffer_pdf) as pdf:
                        fig_table, ax_table = plt.subplots(figsize=(10, 3 + 0.4 * len(stats_affichage)))
                        ax_table.axis("off")
                        ax_table.table(
                            cellText=stats_affichage.values,
                            colLabels=stats_affichage.columns,
                            rowLabels=stats_affichage.index,
                            loc="center",
                        )
                        pdf.savefig(fig_table, bbox_inches="tight")
                        plt.close(fig_table)
                        pdf.savefig(fig_retard, bbox_inches="tight")
                        pdf.savefig(fig_tendance, bbox_inches="tight")
                    buffer_pdf.seek(0)

                    st.download_button(
                        "Export PDF",
                        data=buffer_pdf,
                        file_name="traincker_stats.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

st.markdown(
    '<div class="tk-footer">'
    '<span>© 2026 Traincker</span>'
    '<span class="tk-footer-sep">•</span>'
    '<span>Paul Crémoux</span>'
    '<span class="tk-footer-sep">•</span>'
    '<span class="tk-footer-link">paulcrg</span>'
    "</div>",
    unsafe_allow_html=True,
)
