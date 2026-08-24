"""
Prototype FastAPI + HTMX pour Traincker.

Étape 1 de la migration : recherche de gare + affichage des prochains
départs. Ne touche à rien côté Streamlit (dashboard.py) — coexistence
totale pendant la migration.

Lancer en local :
    uvicorn traincker_web.main:app --reload
"""

from pathlib import Path
import csv
import io
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import matplotlib
matplotlib.use("Agg")  # pas d'interface graphique : on ne fait que générer des PNG
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from traincker.api_client import NavitiaClient, NavitiaAPIError
from traincker.utils import formater_heure, calculer_compte_a_rebours
from traincker.favoris import charger_favoris, sauvegarder_favoris
from traincker.models import Trajet
from traincker.icons import icono, titre_section
from traincker.changelog import CHANGELOG
from traincker.settings import charger_parametres, sauvegarder_parametres
from traincker.theme import css_accessibilite, CSS_THEME_CLAIR
from traincker.journal import ajouter_entree, lire_journal, vider_journal
from traincker.logs import lire_logs, vider_logs
from traincker.db import est_configure, charger_dernier_horodatage
from traincker.tz_utils import parser_horodatage_affichage
from traincker.collector import CSV_PATH
from traincker.analysis import (
    charger_donnees,
    stats_ponctualite_par_ligne,
    stats_ponctualite_par_gare,
    tendance_retard_dans_le_temps,
    heatmap_retards_heure_jour,
    detecter_tendance,
    temps_perdu_cumule_minutes,
    generer_synthese,
    formater_stats_affichage,
)
from traincker.viz import (
    graphe_retard_par_ligne,
    graphe_tendance_temporelle,
    graphe_heatmap_retards,
)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Traincker")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def render(name: str, context: dict):
    """Petit wrapper pour garder l'écriture `render("x.html", {"request":
    request, ...})` partout dans ce fichier, tout en utilisant en interne
    la nouvelle signature Starlette `TemplateResponse(request, name,
    context)` qui évite le DeprecationWarning de l'ancienne forme."""
    request = context["request"]
    contexte_sans_request = {k: v for k, v in context.items() if k != "request"}
    return templates.TemplateResponse(request, name, contexte_sans_request)
templates.env.globals["icono"] = icono
templates.env.globals["titre_section"] = titre_section

# Un seul client Navitia réutilisé pour toute l'app (comme dans le
# dashboard Streamlit).
client = NavitiaClient()

SEUIL_RECHERCHE = 3  # nombre de caractères minimum avant de chercher une gare
LECTURE_SEULE = os.getenv("TRAINCKER_READONLY", "").lower() in ("1", "true", "yes")

# Mode démo publique : ajout de trajets autorisé, mais limité et
# temporaire — pour ouvrir traincker.app au public sans laisser
# n'importe qui accumuler des trajets indéfiniment.
MODE_DEMO = os.getenv("TRAINCKER_DEMO", "").lower() in ("1", "true", "yes")
DEMO_MAX_TRAJETS = 5
DEMO_DUREE_VIE = timedelta(hours=1)

# Même chemin que traincker/monitor.py, dupliqué ici pour ne pas importer
# tout ce module (et ses dépendances schedule/discord-webhook) juste pour
# une constante.
ETAT_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "alertes_envoyees.json"


_cache_kpi = {"valeur": None, "expire": 0.0}
KPI_CACHE_TTL = 30  # secondes


def _stats_rapides() -> dict:
    """KPI du bandeau supérieur — même logique que le dashboard Streamlit :
    Supabase en priorité, sinon le CSV local, avec repli propre si rien
    n'est disponible.

    Mis en cache : sans ça, CHAQUE clic de navigation (Recherche, Favoris,
    Stats, En savoir plus) déclenchait un aller-retour réseau vers Supabase
    rien que pour afficher "Dernière collecte" — la cause principale de la
    latence ressentie en changeant de page.
    """
    maintenant = time.time()
    if _cache_kpi["valeur"] is not None and maintenant < _cache_kpi["expire"]:
        return _cache_kpi["valeur"]

    valeur = _calculer_stats_rapides()
    _cache_kpi["valeur"] = valeur
    _cache_kpi["expire"] = maintenant + KPI_CACHE_TTL
    return valeur


def _calculer_stats_rapides() -> dict:
    """KPI du bandeau supérieur — même logique que le dashboard Streamlit :
    Supabase en priorité, sinon le CSV local, avec repli propre si rien
    n'est disponible."""
    favoris = charger_favoris()
    nb_actifs = sum(1 for t in favoris if t.actif)

    derniere_collecte = "Aucune"
    if est_configure():
        dernier = charger_dernier_horodatage()
        if dernier:
            try:
                derniere_collecte = parser_horodatage_affichage(dernier).strftime("%d/%m %H:%M")
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

    return {
        "trajets_actifs": nb_actifs,
        "derniere_collecte": derniere_collecte,
        "nb_alertes": nb_alertes,
    }


COOKIE_ACCESSIBILITE = "traincker_accessibilite"
ACCESSIBILITE_DEFAUTS = {
    "contraste_eleve": False,
    "taille_police": "normale",
    "theme_clair": False,
    "langue": "fr",
}


def _lire_accessibilite(request: Request) -> dict:
    """Préférences d'accessibilité propres à CE visiteur (cookie), pas
    partagées : sans ça, un visiteur qui passe en thème clair changeait
    l'affichage de tout le monde, y compris des vrais réglages perso."""
    brut = request.cookies.get(COOKIE_ACCESSIBILITE)
    if not brut:
        return ACCESSIBILITE_DEFAUTS.copy()
    try:
        valeurs = json.loads(brut)
    except json.JSONDecodeError:
        return ACCESSIBILITE_DEFAUTS.copy()
    return {**ACCESSIBILITE_DEFAUTS, **{k: v for k, v in valeurs.items() if k in ACCESSIBILITE_DEFAUTS}}


def _ecrire_accessibilite(response: Response, valeurs: dict) -> None:
    response.set_cookie(
        COOKIE_ACCESSIBILITE,
        json.dumps(valeurs),
        max_age=365 * 24 * 3600,
        samesite="lax",
    )


def _contexte_commun(request: Request, page: str) -> dict:
    """Paramètres d'accessibilité (par visiteur, cookie) + KPI à injecter
    dans base.html, calculés à chaque requête."""
    accessibilite = _lire_accessibilite(request)
    theme_clair = accessibilite["theme_clair"]
    return {
        "page": page,
        "lecture_seule": LECTURE_SEULE,
        "css_theme_clair": CSS_THEME_CLAIR if theme_clair else "",
        "css_accessibilite": css_accessibilite(
            accessibilite["contraste_eleve"],
            accessibilite["taille_police"],
        ),
        "logo_fichier": "logo-dark.png" if theme_clair else "logo-white.png",
        "kpi": _stats_rapides(),
        "mode_demo": MODE_DEMO,
        "demo_max_trajets": DEMO_MAX_TRAJETS,
    }


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return render(
        "index.html", {"request": request, **_contexte_commun(request, "recherche")}
    )


@app.get("/gares/suggestions", response_class=HTMLResponse)
def suggestions_gares(request: Request, q: str = ""):
    """Renvoie le fragment HTML des suggestions de gares (déclenché par HTMX
    à chaque frappe dans le champ de recherche, avec un seuil de 3 caractères)."""
    q = q.strip()
    if len(q) < SEUIL_RECHERCHE:
        return render(
            "_suggestions.html",
            {"request": request, "gares": [], "recherche_faite": False},
        )

    try:
        gares = client.search_station(q)
    except NavitiaAPIError:
        gares = []

    return render(
        "_suggestions.html",
        {"request": request, "gares": gares, "recherche_faite": True},
    )


@app.post("/departs", response_class=HTMLResponse)
def departs(request: Request, gare_id: str = Form(...), gare_nom: str = Form("")):
    """Affiche les prochains départs + perturbations pour la gare choisie."""
    try:
        departs_bruts = client.get_next_departures(gare_id)
        perturbations = client.get_disruptions(gare_id)
    except NavitiaAPIError as err:
        return render(
            "_erreur.html", {"request": request, "message": str(err)}
        )

    if not LECTURE_SEULE:
        ajouter_entree("recherche", gare_nom or gare_id)

    departs = [
        {
            "ligne": d["ligne"],
            "direction": d["direction"],
            "heure": formater_heure(d["heure_prevue"]),
            "compte_a_rebours": calculer_compte_a_rebours(d["heure_prevue"]),
            "perturbe": d["statut"] == "realtime"
            and d["heure_theorique"] != d["heure_prevue"],
        }
        for d in departs_bruts
    ]

    return render(
        "_departs.html",
        {
            "request": request,
            "gare_nom": gare_nom,
            "departs": departs,
            "perturbations": perturbations,
        },
    )


# --- Favoris -----------------------------------------------------------

def _charger_favoris_purge() -> list[Trajet]:
    """Charge les favoris et, en mode démo, retire silencieusement ceux
    ajoutés il y a plus d'une heure (uniquement les trajets créés via ce
    mode — reconnaissables à leur champ cree_le — jamais les trajets
    réels d'origine, qui n'ont pas ce champ)."""
    favoris = charger_favoris()
    if not MODE_DEMO:
        return favoris

    maintenant = datetime.now(timezone.utc)
    restants = []
    a_change = False
    for trajet in favoris:
        if trajet.cree_le:
            try:
                cree_le = datetime.fromisoformat(trajet.cree_le)
            except ValueError:
                cree_le = None
            if cree_le and maintenant - cree_le > DEMO_DUREE_VIE:
                a_change = True
                continue
        restants.append(trajet)

    if a_change:
        sauvegarder_favoris(restants)
    return restants


PROCHAIN_DEPART_CACHE_TTL = 20  # secondes : assez court pour rester à jour, assez long pour éviter de re-solliciter l'API SNCF à chaque clic
_cache_prochain_depart: dict[str, tuple[float, dict | None]] = {}


def _prochain_depart_pour(gare_id: str) -> dict | None:
    maintenant = time.time()
    entree = _cache_prochain_depart.get(gare_id)
    if entree and maintenant < entree[0]:
        return entree[1]

    try:
        departs_bruts = client.get_next_departures(gare_id, count=1)
        resultat = None
        if departs_bruts:
            d = departs_bruts[0]
            resultat = {
                "heure": formater_heure(d["heure_prevue"]),
                "compte_a_rebours": calculer_compte_a_rebours(d["heure_prevue"]),
            }
    except NavitiaAPIError:
        resultat = None

    _cache_prochain_depart[gare_id] = (maintenant + PROCHAIN_DEPART_CACHE_TTL, resultat)
    return resultat


def _construire_contexte_favoris() -> list[dict]:
    """Charge les favoris et enrichit chacun avec le prochain départ (si
    actif) et l'info "a déjà un trajet retour", pour le template.

    Les appels API pour le prochain départ de chaque trajet actif sont
    indépendants les uns des autres : on les lance en parallèle (au lieu
    d'un par un) pour ne pas payer N fois la latence réseau sur une page
    qui a plusieurs trajets actifs.
    """
    favoris = _charger_favoris_purge()
    indices_actifs = [i for i, t in enumerate(favoris) if t.actif]

    prochains_departs = {}
    if indices_actifs:
        with ThreadPoolExecutor(max_workers=min(8, len(indices_actifs))) as executor:
            futures = {
                executor.submit(_prochain_depart_pour, favoris[i].gare_depart_id): i
                for i in indices_actifs
            }
            for future in futures:
                prochains_departs[futures[future]] = future.result()

    contexte = []
    for i, trajet in enumerate(favoris):
        a_deja_retour = any(
            f.gare_depart_id == trajet.gare_arrivee_id
            and f.gare_arrivee_id == trajet.gare_depart_id
            for f in favoris
        )

        contexte.append(
            {
                "index": i,
                "trajet": trajet,
                "prochain_depart": prochains_departs.get(i),
                "a_deja_retour": a_deja_retour,
            }
        )
    return contexte


@app.get("/favoris", response_class=HTMLResponse)
def page_favoris(request: Request):
    return render(
        "favoris.html",
        {
            "request": request,
            "favoris": _construire_contexte_favoris(),
            **_contexte_commun(request, "favoris"),
        },
    )


@app.get("/favoris/liste", response_class=HTMLResponse)
def fragment_favoris_liste(request: Request):
    return render(
        "_favoris_liste.html",
        {"request": request, "favoris": _construire_contexte_favoris()},
    )


@app.get("/favoris/gares/suggestions", response_class=HTMLResponse)
def suggestions_gares_favoris(request: Request, champ: str, q: str = ""):
    """Même principe que /gares/suggestions, mais pour le formulaire
    d'ajout de favori (deux champs indépendants : depart / arrivee)."""
    q = q.strip()
    if len(q) < SEUIL_RECHERCHE:
        return render(
            "_favoris_suggestions.html",
            {"request": request, "gares": [], "recherche_faite": False, "champ": champ},
        )

    try:
        gares = client.search_station(q)
    except NavitiaAPIError:
        gares = []

    return render(
        "_favoris_suggestions.html",
        {"request": request, "gares": gares, "recherche_faite": True, "champ": champ},
    )


@app.post("/favoris/ajouter", response_class=HTMLResponse)
def ajouter_favori(
    request: Request,
    nom: str = Form(...),
    gare_depart_id: str = Form(...),
    gare_depart_nom: str = Form(""),
    gare_arrivee_id: str = Form(...),
    gare_arrivee_nom: str = Form(""),
):
    favoris = _charger_favoris_purge()
    nb_trajets_temporaires = sum(1 for t in favoris if t.cree_le)

    if MODE_DEMO and nb_trajets_temporaires >= DEMO_MAX_TRAJETS:
        return render(
            "_favoris_liste.html",
            {
                "request": request,
                "favoris": _construire_contexte_favoris(),
                "erreur_limite": (
                    f"Limite de {DEMO_MAX_TRAJETS} trajets ajoutés atteinte en mode démo "
                    "(les trajets de démonstration ne comptent pas) — supprime-en un ou "
                    "attends qu'un trajet ajouté expire, au bout d'1h."
                ),
            },
        )

    favoris.append(
        Trajet(
            nom=nom.strip(),
            gare_depart_id=gare_depart_id,
            gare_depart_nom=gare_depart_nom,
            gare_arrivee_id=gare_arrivee_id,
            gare_arrivee_nom=gare_arrivee_nom,
            cree_le=datetime.now(timezone.utc).isoformat() if MODE_DEMO else None,
        )
    )
    sauvegarder_favoris(favoris)
    return render(
        "_favoris_liste.html",
        {"request": request, "favoris": _construire_contexte_favoris()},
    )


@app.post("/favoris/{index}/toggle", response_class=HTMLResponse)
def toggle_favori(request: Request, index: int):
    favoris = charger_favoris()
    if 0 <= index < len(favoris):
        favoris[index].actif = not favoris[index].actif
        sauvegarder_favoris(favoris)
    return render(
        "_favoris_liste.html",
        {"request": request, "favoris": _construire_contexte_favoris()},
    )


@app.delete("/favoris/{index}", response_class=HTMLResponse)
def supprimer_favori(request: Request, index: int):
    favoris = charger_favoris()
    if 0 <= index < len(favoris):
        favoris.pop(index)
        sauvegarder_favoris(favoris)
    return render(
        "_favoris_liste.html",
        {"request": request, "favoris": _construire_contexte_favoris()},
    )


@app.post("/favoris/{index}/retour", response_class=HTMLResponse)
def creer_trajet_retour(request: Request, index: int):
    favoris = _charger_favoris_purge()
    if 0 <= index < len(favoris):
        trajet = favoris[index]
        favoris.append(
            Trajet(
                nom=f"{trajet.nom} (retour)",
                gare_depart_id=trajet.gare_arrivee_id,
                gare_depart_nom=trajet.gare_arrivee_nom,
                gare_arrivee_id=trajet.gare_depart_id,
                gare_arrivee_nom=trajet.gare_depart_nom,
                cree_le=datetime.now(timezone.utc).isoformat() if MODE_DEMO else None,
            )
        )
        sauvegarder_favoris(favoris)
    return render(
        "_favoris_liste.html",
        {"request": request, "favoris": _construire_contexte_favoris()},
    )


# --- Statistiques --------------------------------------------------------

# Une vue de /stats déclenche jusqu'à 4 appels à charger_donnees() côté
# navigateur (la page + les 3 <img> de graphiques). Sans cache, ça veut
# dire 4 lectures Supabase (aller-retour réseau) ou 4 reparsing du CSV
# pour un seul affichage. Les données ne changent qu'toutes les 15 min
# (collecte GitHub Actions), donc un cache très court suffit largement.
CACHE_DONNEES_TTL = 30  # secondes
_cache_donnees = {"df": None, "expire": 0.0}


def _charger_donnees_cache():
    maintenant = time.time()
    if _cache_donnees["df"] is None or maintenant >= _cache_donnees["expire"]:
        _cache_donnees["df"] = charger_donnees()
        _cache_donnees["expire"] = maintenant + CACHE_DONNEES_TTL
    return _cache_donnees["df"]


def _invalider_cache_donnees():
    _cache_donnees["df"] = None
    _cache_donnees["expire"] = 0.0


TENDANCE_LIBELLES = {
    "amelioration": "En amélioration",
    "degradation": "En dégradation",
    "stable": "Stable",
}


def _dataframe_vers_lignes(df) -> list[dict]:
    """Transforme un DataFrame pandas (index = ligne/gare) en liste de
    dicts exploitables simplement par Jinja2, colonne d'index incluse."""
    df = df.reset_index()
    return df.to_dict(orient="records")


def _figure_vers_png(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110, transparent=True)
    plt.close(fig)
    return buf.getvalue()


_cache_graphiques: dict[str, tuple[float, bytes]] = {}


def _graphique_png_cache(nom: str, generer) -> Response:
    """Cache les PNG des graphiques (même TTL que les données) : générer
    une figure matplotlib est coûteux en CPU, inutile de le refaire à
    chaque fois que quelqu'un ouvre /stats si les données n'ont pas
    changé depuis moins de 30s."""
    maintenant = time.time()
    entree = _cache_graphiques.get(nom)
    if entree and maintenant < entree[0]:
        return Response(content=entree[1], media_type="image/png")

    contenu = _figure_vers_png(generer())
    _cache_graphiques[nom] = (maintenant + CACHE_DONNEES_TTL, contenu)
    return Response(content=contenu, media_type="image/png")


@app.get("/stats", response_class=HTMLResponse)
def page_stats(request: Request):
    contexte = {"request": request, **_contexte_commun(request, "stats")}

    try:
        df = _charger_donnees_cache()
    except FileNotFoundError as err:
        contexte["message_vide"] = str(err)
        return render("stats.html", contexte)

    stats_ligne = stats_ponctualite_par_ligne(df)
    if stats_ligne.empty:
        contexte["message_vide"] = "Pas encore assez de données collectées pour afficher des statistiques."
        return render("stats.html", contexte)

    stats_gare = stats_ponctualite_par_gare(df)
    pivot = heatmap_retards_heure_jour(df)
    tendance_info = detecter_tendance(df)

    contexte.update(
        {
            "synthese": generer_synthese(stats_ligne),
            "heures_perdues": round(temps_perdu_cumule_minutes(df) / 60, 1),
            "tendance_libelle": (
                TENDANCE_LIBELLES[tendance_info["direction"]] if tendance_info else None
            ),
            "colonnes_ligne": ["Ligne", "Ponctualité", "Retard moyen", "Régularité", "Trains observés"],
            "table_ligne": _dataframe_vers_lignes(formater_stats_affichage(stats_ligne)),
            "colonnes_gare": ["Gare", "Ponctualité", "Retard moyen", "Régularité", "Trains observés"],
            "table_gare": _dataframe_vers_lignes(formater_stats_affichage(stats_gare)),
            "afficher_heatmap": not pivot.dropna(how="all").empty,
        }
    )
    return render("stats.html", contexte)


@app.get("/stats/graphique/retard-ligne.png")
def graphique_retard_ligne():
    def _generer():
        df = _charger_donnees_cache()
        return graphe_retard_par_ligne(stats_ponctualite_par_ligne(df))
    return _graphique_png_cache("retard-ligne", _generer)


@app.get("/stats/graphique/tendance.png")
def graphique_tendance():
    def _generer():
        df = _charger_donnees_cache()
        return graphe_tendance_temporelle(tendance_retard_dans_le_temps(df))
    return _graphique_png_cache("tendance", _generer)


@app.get("/stats/graphique/heatmap.png")
def graphique_heatmap():
    def _generer():
        df = _charger_donnees_cache()
        return graphe_heatmap_retards(heatmap_retards_heure_jour(df))
    return _graphique_png_cache("heatmap", _generer)


@app.get("/stats/export/csv")
def export_stats_csv():
    df = _charger_donnees_cache()
    stats_affichage = formater_stats_affichage(stats_ponctualite_par_ligne(df))
    csv_bytes = stats_affichage.to_csv().encode("utf-8")
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=traincker_stats.csv"},
    )


@app.get("/stats/export/pdf")
def export_stats_pdf():
    df = _charger_donnees_cache()
    stats = stats_ponctualite_par_ligne(df)
    stats_affichage = formater_stats_affichage(stats)
    tendance = tendance_retard_dans_le_temps(df)

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

        fig_retard = graphe_retard_par_ligne(stats)
        pdf.savefig(fig_retard, bbox_inches="tight")
        plt.close(fig_retard)

        fig_tendance = graphe_tendance_temporelle(tendance)
        pdf.savefig(fig_tendance, bbox_inches="tight")
        plt.close(fig_tendance)

    buffer_pdf.seek(0)
    return Response(
        content=buffer_pdf.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=traincker_stats.pdf"},
    )


# --- En savoir plus (socle statique) -------------------------------------

@app.get("/apropos", response_class=HTMLResponse)
def page_apropos(request: Request):
    parametres = {**charger_parametres(), **_lire_accessibilite(request)}
    return render(
        "apropos.html",
        {
            "request": request,
            "changelog": CHANGELOG,
            "parametres": parametres,
            "journal": lire_journal(20),
            "logs": lire_logs(30),
            **_contexte_commun(request, "apropos"),
        },
    )


@app.post("/apropos/parametres/alertes", response_class=HTMLResponse)
def sauver_parametres_alertes(
    request: Request,
    silence_debut: str = Form(""),
    silence_fin: str = Form(""),
    canal_discord: bool = Form(False),
    canal_email: bool = Form(False),
    email_destinataire: str = Form(""),
    alertes_meteo: bool = Form(False),
):
    if LECTURE_SEULE or MODE_DEMO:
        return render(
            "_parametres_resultat.html",
            {"request": request, "erreur": "Modification désactivée sur cette instance."},
        )

    parametres = charger_parametres()
    parametres.update(
        {
            "silence_debut": silence_debut.strip() or parametres["silence_debut"],
            "silence_fin": silence_fin.strip() or parametres["silence_fin"],
            "canal_discord": canal_discord,
            "canal_email": canal_email,
            "email_destinataire": email_destinataire.strip(),
            "alertes_meteo": alertes_meteo,
        }
    )
    sauvegarder_parametres(parametres)
    return render(
        "_parametres_resultat.html", {"request": request, "succes": True}
    )


@app.post("/apropos/parametres/accessibilite")
def sauver_parametres_accessibilite(
    contraste_eleve: bool = Form(False),
    taille_police: str = Form("normale"),
    theme_clair: bool = Form(False),
    langue: str = Form("fr"),
):
    reponse = Response(status_code=204)
    _ecrire_accessibilite(
        reponse,
        {
            "contraste_eleve": contraste_eleve,
            "taille_police": taille_police,
            "theme_clair": theme_clair,
            "langue": langue,
        },
    )
    return reponse


@app.delete("/apropos/journal", response_class=HTMLResponse)
def supprimer_journal(request: Request):
    if not LECTURE_SEULE:
        vider_journal()
    return render(
        "_journal_liste.html",
        {"request": request, "journal": lire_journal(20), "lecture_seule": LECTURE_SEULE},
    )


@app.delete("/apropos/logs", response_class=HTMLResponse)
def supprimer_logs(request: Request):
    if not LECTURE_SEULE:
        vider_logs()
    return render(
        "_logs_liste.html",
        {"request": request, "logs": lire_logs(30), "lecture_seule": LECTURE_SEULE},
    )


def _favoris_vers_export(favoris: list[Trajet]) -> dict:
    return {
        "trajets": [
            {
                "nom": t.nom,
                "gare_depart_id": t.gare_depart_id,
                "gare_depart_nom": t.gare_depart_nom,
                "gare_arrivee_id": t.gare_arrivee_id,
                "gare_arrivee_nom": t.gare_arrivee_nom,
                "actif": t.actif,
            }
            for t in favoris
        ]
    }


@app.get("/apropos/export")
def exporter_favoris_config():
    data = _favoris_vers_export(charger_favoris())
    contenu = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    return Response(
        content=contenu,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=traincker_favoris.json"},
    )


@app.post("/apropos/importer", response_class=HTMLResponse)
async def importer_favoris_config(request: Request, fichier: UploadFile = File(...)):
    if LECTURE_SEULE:
        return render(
            "_import_resultat.html",
            {"request": request, "erreur": "Import désactivé en lecture seule."},
        )

    try:
        contenu = await fichier.read()
        data = json.loads(contenu.decode("utf-8"))
        trajets = [Trajet(**tr) for tr in data.get("trajets", [])]
    except (json.JSONDecodeError, TypeError, KeyError, UnicodeDecodeError) as err:
        return render(
            "_import_resultat.html", {"request": request, "erreur": str(err)}
        )

    sauvegarder_favoris(trajets)
    return render(
        "_import_resultat.html", {"request": request, "succes": True, "nombre": len(trajets)}
    )
