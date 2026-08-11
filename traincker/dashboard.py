"""
Dashboard Streamlit pour Traincker.

Lancer avec :
    streamlit run traincker/dashboard.py
"""

import sys
import os
import base64
import json
import csv
import io
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
# matplotlib est importé plus loin, uniquement dans l'onglet Statistiques :
# c'est une lib lourde, inutile de payer son coût d'import à chaque démarrage
# si l'utilisateur ne consulte jamais les stats.

from traincker.api_client import NavitiaClient, NavitiaAPIError
from traincker.favoris import charger_favoris, sauvegarder_favoris
from traincker.models import Trajet
from traincker.utils import formater_heure, calculer_compte_a_rebours
from traincker.analysis import (
    charger_donnees,
    stats_ponctualite_par_ligne,
    stats_ponctualite_par_gare,
    tendance_retard_dans_le_temps,
    heatmap_retards_heure_jour,
    detecter_tendance,
    temps_perdu_cumule_minutes,
    formater_stats_affichage,
    generer_synthese,
)
from traincker.viz import (
    graphe_retard_par_ligne,
    graphe_tendance_temporelle,
    graphe_heatmap_retards,
)
from traincker.reports import envoyer_rapport_hebdomadaire
from traincker.theme import THEME_CSS, TAB_SLIDER_JS, css_accessibilite, CSS_THEME_CLAIR
from traincker.icons import icono, titre_section
from traincker.monitor import ETAT_PATH
from traincker.collector import CSV_PATH
from traincker.demo_data import DemoNavitiaClient, obtenir_favoris_demo
from traincker.changelog import CHANGELOG
from traincker.settings import charger_parametres, sauvegarder_parametres
from traincker.local_cache import obtenir_meme_expire, enregistrer as cache_enregistrer
from traincker.logs import logger, lire_logs, vider_logs
from traincker.journal import ajouter_entree, lire_journal, vider_journal
from traincker.i18n import t
from traincker.db import charger_departs as db_charger_departs, est_configure as db_configure
from traincker.tz_utils import parser_horodatage_affichage

_favicon_path = Path(__file__).resolve().parent.parent / "assets" / "logo-dashboard-badge.png"

st.set_page_config(
    page_title="Traincker",
    page_icon=str(_favicon_path) if _favicon_path.exists() else None,
    layout="centered",
)
st.markdown(THEME_CSS, unsafe_allow_html=True)

_parametres_globaux = charger_parametres()
_langue = _parametres_globaux.get("langue", "fr")

if _parametres_globaux.get("theme_clair", False):
    st.markdown(CSS_THEME_CLAIR, unsafe_allow_html=True)

st.markdown(
    css_accessibilite(
        _parametres_globaux.get("contraste_eleve", False),
        _parametres_globaux.get("taille_police", "normale"),
    ),
    unsafe_allow_html=True,
)

FORCE_DEMO = os.getenv("TRAINCKER_FORCE_DEMO", "").lower() in ("1", "true", "yes")

if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = FORCE_DEMO
if "mode_degrade" not in st.session_state:
    st.session_state.mode_degrade = None


def get_client():
    if st.session_state.demo_mode:
        return DemoNavitiaClient()
    return NavitiaClient()


def get_favoris():
    if st.session_state.demo_mode:
        if "demo_favoris" not in st.session_state:
            st.session_state.demo_favoris = obtenir_favoris_demo()
        return st.session_state.demo_favoris
    return charger_favoris()


def save_favoris(favoris_liste):
    if st.session_state.demo_mode:
        st.session_state.demo_favoris = favoris_liste
    else:
        sauvegarder_favoris(favoris_liste)


@st.cache_data(ttl=120, show_spinner=False)
def rechercher_gares_cache(query: str):
    cle = f"recherche:{query.lower()}"
    try:
        client = get_client()
        resultat = client.search_station(query)
        if not st.session_state.demo_mode:
            cache_enregistrer(cle, resultat)
        st.session_state.mode_degrade = None
        return resultat
    except NavitiaAPIError:
        secours = obtenir_meme_expire(cle)
        if secours:
            valeur, horodatage = secours
            st.session_state.mode_degrade = horodatage
            logger(f"Mode dégradé activé pour la recherche « {query} »", niveau="WARNING")
            return valeur
        raise


@st.cache_data(ttl=20, show_spinner=False)
def obtenir_departs_et_perturbations_gare(station_id: str):
    cle = f"departs:{station_id}"
    try:
        client = get_client()
        departs = client.get_next_departures(station_id, count=10)
        perturbations = client.get_disruptions(station_id)
        resultat = (departs, perturbations)
        if not st.session_state.demo_mode:
            cache_enregistrer(cle, resultat)
        st.session_state.mode_degrade = None
        return resultat
    except NavitiaAPIError:
        secours = obtenir_meme_expire(cle)
        if secours:
            valeur, horodatage = secours
            st.session_state.mode_degrade = horodatage
            logger(f"Mode dégradé activé pour la gare {station_id}", niveau="WARNING")
            return tuple(valeur)
        raise


@st.cache_data(ttl=30, show_spinner=False)
def obtenir_next_depart_et_perturbations(gare_depart_id: str, gare_arrivee_id: str):
    cle = f"favori:{gare_depart_id}:{gare_arrivee_id}"
    try:
        client = get_client()
        departs = client.get_next_departures(gare_depart_id, count=1)
        perturbations = client.get_disruptions(gare_depart_id)
        perturbations += client.get_disruptions(gare_arrivee_id)
        depart = departs[0] if departs else None
        resultat = (depart, perturbations)
        if not st.session_state.demo_mode:
            cache_enregistrer(cle, resultat)
        return resultat
    except NavitiaAPIError:
        secours = obtenir_meme_expire(cle)
        if secours:
            valeur, _ = secours
            logger(f"Mode dégradé activé pour le trajet {gare_depart_id}->{gare_arrivee_id}", niveau="WARNING")
            return tuple(valeur)
        return None, []


@st.cache_data(ttl=300, show_spinner=False)
def obtenir_donnees_stats():
    """Pipeline stats mis en cache : évite de recalculer à chaque interaction
    ailleurs dans l'app (Streamlit ré-exécute tous les onglets à chaque clic)."""
    df = charger_donnees()
    return {
        "stats_ligne": stats_ponctualite_par_ligne(df),
        "stats_gare": stats_ponctualite_par_gare(df),
        "tendance_temporelle": tendance_retard_dans_le_temps(df),
        "pivot_heatmap": heatmap_retards_heure_jour(df),
        "tendance_info": detecter_tendance(df),
        "temps_perdu": temps_perdu_cumule_minutes(df),
    }


def obtenir_infos_favoris(favoris: list) -> list:
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
    resultat = None
    with st.container(key=f"suggest_box_{cle}"):
        for s in stations:
            if st.button(s["name"], key=f"sugg_{cle}_{s['id']}", use_container_width=True):
                resultat = s
    return resultat


_nom_logo = "logo-dark.png" if _parametres_globaux.get("theme_clair", False) else "logo-white.png"
_logo_path = Path(__file__).resolve().parent.parent / "assets" / _nom_logo
if _logo_path.exists():
    _logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode()
    st.markdown(
        f'<div class="tk-logo-wrap"><img src="data:image/png;base64,{_logo_b64}" alt="Traincker" style="height:46px;"></div>',
        unsafe_allow_html=True,
    )
else:
    st.title("Traincker")

st.markdown(f'<p class="tk-caption">{t("caption", _langue)}</p>', unsafe_allow_html=True)

if not FORCE_DEMO:
    col_demo_spacer, col_demo_toggle = st.columns([4, 2])
    with col_demo_toggle:
        demo_actif = st.toggle(
            "Mode démo (données fictives)",
            value=st.session_state.demo_mode,
            key="demo_toggle",
            help="Utilise des données inventées, sans appeler l'API SNCF ni exposer de clé réelle.",
        )
        if demo_actif != st.session_state.demo_mode:
            st.session_state.demo_mode = demo_actif
            rechercher_gares_cache.clear()
            obtenir_departs_et_perturbations_gare.clear()
            obtenir_next_depart_et_perturbations.clear()
            st.rerun()

if st.session_state.demo_mode:
    _texte_demo = (
        "Site de démonstration — toutes les données affichées sont fictives, "
        "aucune clé API réelle n'est utilisée ici."
        if FORCE_DEMO else t("mode_demo_actif", _langue)
    )
    st.markdown(f'<div class="tk-banner-alert">{_texte_demo}</div>', unsafe_allow_html=True)

if st.session_state.mode_degrade:
    _dt_secours = datetime.fromtimestamp(st.session_state.mode_degrade)
    st.markdown(
        f'<div class="tk-banner-degrade">Mode dégradé — l\'API SNCF ne répond pas. '
        f'Dernières données connues du {_dt_secours:%d/%m à %H:%M}.</div>',
        unsafe_allow_html=True,
    )


def obtenir_stats_rapides() -> dict:
    """
    Retourne les KPI en tête de dashboard. Lit Supabase en priorité si
    configuré (nécessaire pour que le site hébergé sur Render affiche des
    données à jour) ; les horodatages sont convertis en heure de Paris,
    quelle que soit leur origine (corrige le décalage -2h observé quand le
    serveur tourne en UTC).
    """
    favoris = get_favoris()
    nb_actifs = sum(1 for t_ in favoris if t_.actif)

    derniere_collecte = "Aucune"
    if db_configure():
        lignes = db_charger_departs()
        if lignes:
            try:
                dernier = max(lignes, key=lambda l: l["horodatage_collecte"])
                dt = parser_horodatage_affichage(dernier["horodatage_collecte"])
                derniere_collecte = dt.strftime("%d/%m %H:%M")
            except (KeyError, ValueError):
                pass
    elif CSV_PATH.exists():
        try:
            with open(CSV_PATH, encoding="utf-8") as f:
                lignes = list(csv.DictReader(f))
            if lignes:
                dt = parser_horodatage_affichage(lignes[-1]["horodatage_collecte"])
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

    return {"trajets_actifs": nb_actifs, "derniere_collecte": derniere_collecte, "nb_alertes": nb_alertes}


_stats_rapides = obtenir_stats_rapides()
st.markdown(
    f"""
    <div class="tk-chip-row">
        <div class="tk-chip"><span class="tk-chip-label">{t("chip_trajets_actifs", _langue)}</span><span class="tk-chip-value">{_stats_rapides['trajets_actifs']}</span></div>
        <div class="tk-chip"><span class="tk-chip-label">{t("chip_derniere_collecte", _langue)}</span><span class="tk-chip-value">{_stats_rapides['derniere_collecte']}</span></div>
        <div class="tk-chip"><span class="tk-chip-label">{t("chip_alertes", _langue)}</span><span class="tk-chip-value">{_stats_rapides['nb_alertes']}</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

_favoris_globaux = get_favoris()
_infos_favoris = obtenir_infos_favoris(_favoris_globaux)
_favoris_perturbes = [info for info in _infos_favoris if info["perturbations"]]

if _favoris_perturbes:
    _lignes_banniere = "<br>".join(
        f'<span class="tk-dot tk-dot-alert"></span><strong>{info["trajet"].nom}</strong> : {info["perturbations"][0]["titre"]}'
        for info in _favoris_perturbes
    )
    st.markdown(
        f'<div class="tk-banner-alert">{icono("alert", size=18)} Perturbation en cours sur un trajet favori<br>{_lignes_banniere}</div>',
        unsafe_allow_html=True,
    )

tab_recherche, tab_favoris, tab_stats, tab_apropos = st.tabs(
    [t("tab_recherche", _langue), t("tab_favoris", _langue), t("tab_stats", _langue), t("tab_apropos", _langue)]
)
st.markdown(TAB_SLIDER_JS, unsafe_allow_html=True)

with tab_recherche:
    with st.container(border=True, key="card_recherche"):
        st.markdown(titre_section("search", t("prochains_departs", _langue)), unsafe_allow_html=True)
        st.markdown(
            '<p class="tk-hint">Tape le nom d\'une gare (3 caractères minimum) pour voir ses prochains départs.</p>',
            unsafe_allow_html=True,
        )

        if "historique_recherches" not in st.session_state:
            st.session_state.historique_recherches = []
        if "station_recherche" not in st.session_state:
            st.session_state.station_recherche = None
        if "gare_input_pendiente" in st.session_state:
            st.session_state["gare_input"] = st.session_state.pop("gare_input_pendiente")

        col_input, col_refresh = st.columns([5, 1])
        with col_input:
            gare_input = st.text_input(
                "Nom de la gare", placeholder="ex: Paris (min. 3 caractères)",
                key="gare_input", label_visibility="collapsed",
            )
        with col_refresh:
            if st.button(t("rafraichir", _langue), key="refresh_recherche", use_container_width=True):
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
                    tableau_departs = pd.DataFrame([
                        {
                            "Ligne": d["ligne"], "Direction": d["direction"],
                            "Départ": formater_heure(d["heure_prevue"]),
                            "Statut": "Temps réel" if d["statut"] == "realtime" else "Théorique",
                        }
                        for d in departs
                    ])
                    st.dataframe(tableau_departs, hide_index=True, use_container_width=True)

                if disruptions:
                    st.markdown(
                        f'<p class="tk-status-line"><span class="tk-dot tk-dot-alert"></span>{t("perturbations_en_cours", _langue)}</p>',
                        unsafe_allow_html=True,
                    )
                    for p in disruptions:
                        st.write(f"- **{p['titre']}** : {p['message']}")
                else:
                    st.markdown(
                        f'<p class="tk-status-line"><span class="tk-dot tk-dot-ok"></span>{t("aucune_perturbation", _langue)}</p>',
                        unsafe_allow_html=True,
                    )

                hist = st.session_state.historique_recherches
                hist = [h for h in hist if h["id"] != station["id"]]
                hist.insert(0, station)
                st.session_state.historique_recherches = hist[:5]

                if "journal_ids_logues" not in st.session_state:
                    st.session_state.journal_ids_logues = set()
                if not st.session_state.demo_mode and station["id"] not in st.session_state.journal_ids_logues:
                    ajouter_entree("recherche", station["name"])
                    st.session_state.journal_ids_logues.add(station["id"])

            except NavitiaAPIError as e:
                st.error(f"Erreur API : {e}")
                logger(f"Erreur API sur la recherche « {gare_input} » : {e}", niveau="ERROR")

with tab_favoris:
    with st.container(border=True, key="card_favoris_liste"):
        st.markdown(titre_section("star", t("trajets_favoris", _langue)), unsafe_allow_html=True)

        if not _infos_favoris:
            st.info("Aucun trajet favori configuré pour l'instant. Ajoutes-en un ci-dessous.")
        else:
            for i, info in enumerate(_infos_favoris):
                trajet = info["trajet"]
                col_dot, col_info, col_toggle, col_delete = st.columns([0.35, 4.15, 1.25, 1.25], gap="small")

                with col_dot:
                    dot_class = "tk-dot-ok" if trajet.actif else "tk-dot-alert"
                    st.markdown(f'<span class="tk-dot {dot_class}" style="margin-top:14px;"></span>', unsafe_allow_html=True)

                with col_info:
                    st.write(f"**{trajet.nom}** : {trajet.gare_depart_nom} → {trajet.gare_arrivee_nom}")
                    if trajet.actif and info["prochain_depart"]:
                        depart = info["prochain_depart"]
                        heure = formater_heure(depart["heure_prevue"])
                        countdown = calculer_compte_a_rebours(depart["heure_prevue"])
                        st.markdown(
                            f'<div class="tk-next-train"><span class="tk-next-train-time">{heure}</span>'
                            f'<span class="tk-next-train-countdown">{countdown}</span></div>',
                            unsafe_allow_html=True,
                        )

                with col_toggle:
                    st.markdown('<div class="tk-compact-btn">', unsafe_allow_html=True)
                    label_toggle = "Désactiver" if trajet.actif else "Activer"
                    if st.button(label_toggle, key=f"toggle_{i}", use_container_width=True):
                        favoris_maj = get_favoris()
                        favoris_maj[i].actif = not favoris_maj[i].actif
                        save_favoris(favoris_maj)
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
                        f'<p class="tk-confirm-text">Supprimer « {trajet.nom} » ? Cette action est irréversible.</p>',
                        unsafe_allow_html=True,
                    )
                    col_confirm, col_annuler, _ = st.columns([1, 1, 3])
                    with col_confirm:
                        if st.button("Confirmer", key=f"confirm_yes_{i}", use_container_width=True):
                            favoris_maj = get_favoris()
                            favoris_maj.pop(i)
                            save_favoris(favoris_maj)
                            st.session_state[f"confirm_delete_{i}"] = False
                            st.rerun()
                    with col_annuler:
                        if st.button("Annuler", key=f"confirm_no_{i}", use_container_width=True):
                            st.session_state[f"confirm_delete_{i}"] = False
                            st.rerun()

                deja_un_retour = any(
                    f.gare_depart_id == trajet.gare_arrivee_id and f.gare_arrivee_id == trajet.gare_depart_id
                    for f in get_favoris()
                )
                if not deja_un_retour:
                    if st.button("Créer le trajet retour", key=f"retour_{i}", help="Ajoute le trajet inverse"):
                        favoris_maj = get_favoris()
                        favoris_maj.append(Trajet(
                            nom=f"{trajet.nom} (retour)",
                            gare_depart_id=trajet.gare_arrivee_id, gare_depart_nom=trajet.gare_arrivee_nom,
                            gare_arrivee_id=trajet.gare_depart_id, gare_arrivee_nom=trajet.gare_depart_nom,
                        ))
                        save_favoris(favoris_maj)
                        st.success("Trajet retour ajouté.")
                        st.rerun()

                if i < len(_infos_favoris) - 1:
                    st.markdown('<div class="tk-divider"></div>', unsafe_allow_html=True)

    with st.container(border=True, key="card_favoris_ajout"):
        st.markdown(titre_section("plus", t("ajouter_trajet", _langue)), unsafe_allow_html=True)
        st.markdown(
            '<p class="tk-hint">Cherche une gare de départ et d\'arrivée, clique sur une suggestion, puis valide.</p>',
            unsafe_allow_html=True,
        )

        nom_trajet = st.text_input("Nom du trajet", placeholder="ex: Trajet du matin", key="nom_trajet_input")

        for cle_gare, label_gare, placeholder_gare in [
            ("depart", "Gare de départ", "ex: Paris"),
            ("arrivee", "Gare d'arrivée", "ex: Marseille"),
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

        if gare_depart_choisie and gare_arrivee_choisie:
            if st.button("Inverser départ / arrivée", key="inverser_depart_arrivee"):
                st.session_state["station_depart"] = gare_arrivee_choisie
                st.session_state["station_arrivee"] = gare_depart_choisie
                st.rerun()

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
                favoris_maj = get_favoris()
                favoris_maj.append(Trajet(
                    nom=nom_trajet,
                    gare_depart_id=gare_depart_choisie["id"], gare_depart_nom=gare_depart_choisie["name"],
                    gare_arrivee_id=gare_arrivee_choisie["id"], gare_arrivee_nom=gare_arrivee_choisie["name"],
                ))
                save_favoris(favoris_maj)
                st.session_state["station_depart"] = None
                st.session_state["station_arrivee"] = None
                if not st.session_state.demo_mode:
                    ajouter_entree("ajout_favori", nom_trajet)
                st.success(f"Trajet « {nom_trajet} » ajouté !")
                st.rerun()

with tab_stats:
    with st.container(border=True, key="card_stats"):
        st.markdown(titre_section("chart", t("statistiques_ponctualite", _langue)), unsafe_allow_html=True)

        try:
            donnees_stats = obtenir_donnees_stats()
        except FileNotFoundError:
            st.info(
                "Aucune donnée historisée pour l'instant. Lance "
                "`python main.py surveiller` un moment pour commencer à collecter des données."
            )
        else:
            stats = donnees_stats["stats_ligne"]
            if stats.empty:
                st.info("Pas encore assez de données exploitables pour calculer des stats.")
            else:
                import matplotlib.pyplot as plt
                from matplotlib.backends.backend_pdf import PdfPages

                stats_affichage = formater_stats_affichage(stats)

                synthese = generer_synthese(stats)
                if synthese:
                    st.markdown(f'<div class="tk-insight">{synthese}</div>', unsafe_allow_html=True)

                temps_perdu = donnees_stats["temps_perdu"]
                tendance_info = donnees_stats["tendance_info"]

                col_temps_perdu, col_tendance = st.columns(2)
                with col_temps_perdu:
                    heures_perdues = temps_perdu / 60
                    st.markdown(
                        f'<div class="tk-chip"><span class="tk-chip-label">Temps de retard cumulé</span>'
                        f'<span class="tk-chip-value">{heures_perdues:.1f} h</span></div>',
                        unsafe_allow_html=True,
                    )
                with col_tendance:
                    if tendance_info:
                        libelles = {"amelioration": "En amélioration", "degradation": "En dégradation", "stable": "Stable"}
                        st.markdown(
                            f'<div class="tk-chip"><span class="tk-chip-label">Tendance récente</span>'
                            f'<span class="tk-chip-value">{libelles[tendance_info["direction"]]}</span></div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            '<div class="tk-chip"><span class="tk-chip-label">Tendance récente</span>'
                            '<span class="tk-chip-value">Pas assez de données</span></div>',
                            unsafe_allow_html=True,
                        )
                st.markdown("<br>", unsafe_allow_html=True)

                st.dataframe(
                    stats_affichage, use_container_width=True,
                    column_config={
                        "Ponctualité": st.column_config.TextColumn(help="Part des trains partis avec moins de 5 min de retard"),
                        "Retard moyen": st.column_config.TextColumn(help="Retard moyen constaté sur la ligne"),
                        "Régularité": st.column_config.TextColumn(help="Écart-type du retard : plus c'est bas, plus la ligne est régulière"),
                        "Trains observés": st.column_config.NumberColumn(help="Nombre de départs historisés pour cette ligne"),
                    },
                )
                st.markdown(
                    '<p class="tk-legend">Un train est considéré « à l\'heure » s\'il part avec moins de 5 minutes de retard.</p>',
                    unsafe_allow_html=True,
                )

                st.subheader("Retard moyen par ligne")
                fig_retard = graphe_retard_par_ligne(stats)
                st.pyplot(fig_retard)

                st.subheader("Évolution du retard moyen dans le temps")
                fig_tendance = graphe_tendance_temporelle(donnees_stats["tendance_temporelle"])
                st.pyplot(fig_tendance)

                st.divider()
                st.subheader("Fiabilité par gare")
                st.dataframe(formater_stats_affichage(donnees_stats["stats_gare"]), use_container_width=True)

                st.subheader("Répartition des retards (jour x heure)")
                pivot = donnees_stats["pivot_heatmap"]
                if pivot.dropna(how="all").empty:
                    st.caption("Pas encore assez de données pour cette vue.")
                else:
                    fig_heatmap = graphe_heatmap_retards(pivot)
                    st.pyplot(fig_heatmap)

                st.divider()
                st.markdown(titre_section("download", "Exporter"), unsafe_allow_html=True)
                col_csv, col_pdf = st.columns(2)

                with col_csv:
                    csv_bytes = stats_affichage.to_csv().encode("utf-8")
                    st.download_button(
                        "Export CSV", data=csv_bytes, file_name="traincker_stats.csv",
                        mime="text/csv", use_container_width=True,
                    )

                with col_pdf:
                    buffer_pdf = io.BytesIO()
                    with PdfPages(buffer_pdf) as pdf:
                        fig_table, ax_table = plt.subplots(figsize=(10, 3 + 0.4 * len(stats_affichage)))
                        ax_table.axis("off")
                        ax_table.table(
                            cellText=stats_affichage.values, colLabels=stats_affichage.columns,
                            rowLabels=stats_affichage.index, loc="center",
                        )
                        pdf.savefig(fig_table, bbox_inches="tight")
                        plt.close(fig_table)
                        pdf.savefig(fig_retard, bbox_inches="tight")
                        pdf.savefig(fig_tendance, bbox_inches="tight")
                    buffer_pdf.seek(0)

                    st.download_button(
                        "Export PDF", data=buffer_pdf, file_name="traincker_stats.pdf",
                        mime="application/pdf", use_container_width=True,
                    )

with tab_apropos:
    with st.container(border=True, key="card_apropos"):
        st.markdown(titre_section("pin", t("en_savoir_plus_titre", _langue)), unsafe_allow_html=True)
        st.markdown("À compléter.")

    with st.container(border=True, key="card_portfolio"):
        st.markdown(titre_section("shield", t("vue_technique", _langue)), unsafe_allow_html=True)
        st.markdown(
            """
**Stack** : Python, Streamlit, pandas/numpy, matplotlib, API SNCF (Navitia), Open-Meteo, Supabase.

**Architecture** :
- `api_client.py` — client HTTP vers l'API SNCF, avec timeout et gestion d'erreurs
- `monitor.py` — surveillance périodique, alertes Discord/email, heures de silence
- `analysis.py` / `viz.py` — statistiques de ponctualité et visualisations
- `dashboard.py` — interface Streamlit (recherche, favoris, statistiques)
- `db.py` — persistance partagée Supabase entre la surveillance et le dashboard hébergé

**Points notables** : mode démo avec données fictives, mode dégradé en cas de panne API,
suite de tests automatisés (pytest), déploiement continu (GitHub Actions + Render).
            """
        )
        st.link_button("Voir le code sur GitHub", "https://github.com/paulcrg/traincker", use_container_width=True)

    with st.container(border=True, key="card_changelog"):
        st.markdown(titre_section("clock", t("historique_evolutions", _langue)), unsafe_allow_html=True)
        for entree in CHANGELOG:
            st.markdown(f"**{entree['titre']}**")
            st.caption(entree["description"])

    with st.container(border=True, key="card_config"):
        st.markdown(titre_section("download", t("sauvegarde_config_title", _langue)), unsafe_allow_html=True)
        st.markdown(f'<p class="tk-hint">{t("sauvegarde_config_hint", _langue)}</p>', unsafe_allow_html=True)

        col_export, col_import = st.columns(2)
        with col_export:
            favoris_export = get_favoris()
            export_data = {"trajets": [
                {"nom": t_.nom, "gare_depart_id": t_.gare_depart_id, "gare_depart_nom": t_.gare_depart_nom,
                 "gare_arrivee_id": t_.gare_arrivee_id, "gare_arrivee_nom": t_.gare_arrivee_nom, "actif": t_.actif}
                for t_ in favoris_export
            ]}
            st.download_button(
                t("exporter_trajets", _langue), data=json.dumps(export_data, ensure_ascii=False, indent=2),
                file_name="traincker_favoris.json", mime="application/json",
                use_container_width=True, disabled=st.session_state.demo_mode,
            )

        with col_import:
            fichier_import = st.file_uploader(
                "Restaurer", type="json", label_visibility="collapsed", disabled=st.session_state.demo_mode,
            )
            if fichier_import is not None:
                try:
                    data_importee = json.loads(fichier_import.read().decode("utf-8"))
                    trajets_importes = [Trajet(**tr) for tr in data_importee.get("trajets", [])]
                    if st.button(t("confirmer_restauration", _langue), type="primary"):
                        save_favoris(trajets_importes)
                        st.success(f"{len(trajets_importes)} trajet(s) restauré(s).")
                        st.rerun()
                except (json.JSONDecodeError, TypeError, KeyError) as e:
                    st.error(f"Fichier invalide : {e}")

        if st.session_state.demo_mode:
            st.caption("Export/import désactivés en mode démo.")

    with st.container(border=True, key="card_alertes"):
        st.markdown(titre_section("alert", t("parametres_alerte", _langue)), unsafe_allow_html=True)
        st.markdown(f'<p class="tk-hint">{t("parametres_alerte_hint", _langue)}</p>', unsafe_allow_html=True)

        col_silence_debut, col_silence_fin = st.columns(2)
        with col_silence_debut:
            heure_debut = st.text_input(t("silence_a_partir_de", _langue), value=_parametres_globaux["silence_debut"], key="param_silence_debut")
        with col_silence_fin:
            heure_fin = st.text_input(t("silence_jusqua", _langue), value=_parametres_globaux["silence_fin"], key="param_silence_fin")
        st.caption(t("note_perturbations_critiques", _langue))

        canal_discord = st.checkbox(t("alertes_discord_label", _langue), value=_parametres_globaux["canal_discord"], key="param_discord")
        canal_email = st.checkbox(t("alertes_email_label", _langue), value=_parametres_globaux["canal_email"], key="param_email")
        email_destinataire = st.text_input(
            t("adresse_email_label", _langue), value=_parametres_globaux["email_destinataire"],
            key="param_email_dest", disabled=not canal_email, placeholder="toi@exemple.com",
        )
        alertes_meteo = st.checkbox(t("alertes_meteo_label", _langue), value=_parametres_globaux["alertes_meteo"], key="param_meteo")

        if st.button(t("enregistrer_parametres", _langue), type="primary"):
            maj = charger_parametres()
            maj.update({
                "silence_debut": heure_debut, "silence_fin": heure_fin,
                "canal_discord": canal_discord, "canal_email": canal_email,
                "email_destinataire": email_destinataire, "alertes_meteo": alertes_meteo,
            })
            sauvegarder_parametres(maj)
            st.success("Paramètres enregistrés.")

        st.divider()
        st.caption(t("note_rapport_hebdo", _langue))
        if st.button(t("envoyer_rapport", _langue)):
            if not st.session_state.demo_mode:
                envoye = envoyer_rapport_hebdomadaire()
                if envoye:
                    st.success("Rapport envoyé.")
                else:
                    st.warning("Active les alertes email et renseigne une adresse d'abord.")
            else:
                st.info("Indisponible en mode démo.")

    with st.container(border=True, key="card_accessibilite"):
        st.markdown(titre_section("eye", t("accessibilite", _langue)), unsafe_allow_html=True)
        st.markdown(f'<p class="tk-hint">{t("applique_immediat", _langue)}</p>', unsafe_allow_html=True)

        col_contraste, col_police = st.columns(2)
        with col_contraste:
            contraste_eleve = st.checkbox(t("contraste_eleve_label", _langue), value=_parametres_globaux.get("contraste_eleve", False), key="param_contraste")
        with col_police:
            taille_police = st.selectbox(
                t("taille_texte", _langue), options=["normale", "grande", "tres_grande"],
                index=["normale", "grande", "tres_grande"].index(_parametres_globaux.get("taille_police", "normale")),
                format_func=lambda v: {"normale": t("taille_normale", _langue), "grande": t("taille_grande", _langue), "tres_grande": t("taille_tres_grande", _langue)}[v],
                key="param_taille_police",
            )

        col_theme, col_langue = st.columns(2)
        with col_theme:
            theme_clair = st.checkbox(t("theme_clair", _langue), value=_parametres_globaux.get("theme_clair", False), key="param_theme_clair")
        with col_langue:
            langues_disponibles = ["fr", "en", "de", "no", "sv"]
            langue_choisie = st.selectbox(
                t("langue", _langue), options=langues_disponibles,
                index=langues_disponibles.index(_parametres_globaux.get("langue", "fr")),
                format_func=lambda v: {"fr": "Français", "en": "English", "de": "Deutsch", "no": "Norsk", "sv": "Svenska"}[v],
                key="param_langue",
            )

        _valeurs_access_actuelles = {"contraste_eleve": contraste_eleve, "taille_police": taille_police, "theme_clair": theme_clair, "langue": langue_choisie}
        _valeurs_access_sauvees = {cle: _parametres_globaux.get(cle) for cle in _valeurs_access_actuelles}
        if _valeurs_access_actuelles != _valeurs_access_sauvees:
            _maj_access = charger_parametres()
            _maj_access.update(_valeurs_access_actuelles)
            sauvegarder_parametres(_maj_access)
            st.rerun()

    with st.container(border=True, key="card_historique"):
        st.markdown(titre_section("list", t("mon_historique", _langue)), unsafe_allow_html=True)
        st.markdown(f'<p class="tk-hint">{t("historique_hint", _langue)}</p>', unsafe_allow_html=True)

        if st.session_state.demo_mode:
            st.caption("Historique désactivé en mode démo.")
        else:
            entrees = lire_journal(limite=20)
            if not entrees:
                st.info(t("historique_vide", _langue))
            else:
                LIBELLES_JOURNAL = {"recherche": "Recherche", "ajout_favori": "Trajet ajouté"}
                for entree in entrees:
                    dt = datetime.fromisoformat(entree["horodatage"])
                    label = LIBELLES_JOURNAL.get(entree["type"], entree["type"])
                    st.markdown(f'<div class="tk-log-line">{dt:%d/%m %H:%M} — {label} : {entree["detail"]}</div>', unsafe_allow_html=True)
                if st.button(t("vider_historique", _langue), key="vider_historique"):
                    vider_journal()
                    st.rerun()

    with st.container(border=True, key="card_logs"):
        st.markdown(titre_section("shield", t("journal_technique", _langue)), unsafe_allow_html=True)
        st.markdown(f'<p class="tk-hint">{t("journal_hint", _langue)}</p>', unsafe_allow_html=True)

        lignes_log = lire_logs(nb_lignes=30)
        if not lignes_log:
            st.info(t("aucun_evenement", _langue))
        else:
            for ligne in lignes_log:
                st.markdown(f'<div class="tk-log-line">{ligne.strip()}</div>', unsafe_allow_html=True)
            if st.button(t("vider_logs", _langue), key="vider_logs"):
                vider_logs()
                st.rerun()

    with st.container(border=True, key="card_support"):
        st.markdown(titre_section("alert", t("un_probleme", _langue)), unsafe_allow_html=True)
        url_issue = (
            "https://github.com/paulcrg/traincker/issues/new"
            "?title=Bug%20signal%C3%A9%20depuis%20le%20dashboard"
            "&body=Décris%20le%20problème%20rencontré%20ici."
        )
        st.link_button(t("signaler_bug", _langue), url_issue, use_container_width=True)

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
