"""
Prototype FastAPI + HTMX pour Traincker.

Étape 1 de la migration : recherche de gare + affichage des prochains
départs. Ne touche à rien côté Streamlit (dashboard.py) — coexistence
totale pendant la migration.

Lancer en local :
    uvicorn traincker_web.main:app --reload
"""

from pathlib import Path
import io

from fastapi import FastAPI, Request, Form
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
templates.env.globals["icono"] = icono
templates.env.globals["titre_section"] = titre_section

# Un seul client Navitia réutilisé pour toute l'app (comme dans le
# dashboard Streamlit).
client = NavitiaClient()

SEUIL_RECHERCHE = 3  # nombre de caractères minimum avant de chercher une gare


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "page": "recherche"}
    )


@app.get("/gares/suggestions", response_class=HTMLResponse)
def suggestions_gares(request: Request, q: str = ""):
    """Renvoie le fragment HTML des suggestions de gares (déclenché par HTMX
    à chaque frappe dans le champ de recherche, avec un seuil de 3 caractères)."""
    q = q.strip()
    if len(q) < SEUIL_RECHERCHE:
        return templates.TemplateResponse(
            "_suggestions.html",
            {"request": request, "gares": [], "recherche_faite": False},
        )

    try:
        gares = client.search_station(q)
    except NavitiaAPIError:
        gares = []

    return templates.TemplateResponse(
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
        return templates.TemplateResponse(
            "_erreur.html", {"request": request, "message": str(err)}
        )

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

    return templates.TemplateResponse(
        "_departs.html",
        {
            "request": request,
            "gare_nom": gare_nom,
            "departs": departs,
            "perturbations": perturbations,
        },
    )


# --- Favoris -----------------------------------------------------------

def _construire_contexte_favoris() -> list[dict]:
    """Charge les favoris et enrichit chacun avec le prochain départ (si
    actif) et l'info "a déjà un trajet retour", pour le template."""
    favoris = charger_favoris()
    contexte = []
    for i, trajet in enumerate(favoris):
        prochain_depart = None
        if trajet.actif:
            try:
                departs_bruts = client.get_next_departures(
                    trajet.gare_depart_id, count=1
                )
                if departs_bruts:
                    d = departs_bruts[0]
                    prochain_depart = {
                        "heure": formater_heure(d["heure_prevue"]),
                        "compte_a_rebours": calculer_compte_a_rebours(
                            d["heure_prevue"]
                        ),
                    }
            except NavitiaAPIError:
                pass

        a_deja_retour = any(
            f.gare_depart_id == trajet.gare_arrivee_id
            and f.gare_arrivee_id == trajet.gare_depart_id
            for f in favoris
        )

        contexte.append(
            {
                "index": i,
                "trajet": trajet,
                "prochain_depart": prochain_depart,
                "a_deja_retour": a_deja_retour,
            }
        )
    return contexte


@app.get("/favoris", response_class=HTMLResponse)
def page_favoris(request: Request):
    return templates.TemplateResponse(
        "favoris.html",
        {
            "request": request,
            "page": "favoris",
            "favoris": _construire_contexte_favoris(),
        },
    )


@app.get("/favoris/liste", response_class=HTMLResponse)
def fragment_favoris_liste(request: Request):
    return templates.TemplateResponse(
        "_favoris_liste.html",
        {"request": request, "favoris": _construire_contexte_favoris()},
    )


@app.get("/favoris/gares/suggestions", response_class=HTMLResponse)
def suggestions_gares_favoris(request: Request, champ: str, q: str = ""):
    """Même principe que /gares/suggestions, mais pour le formulaire
    d'ajout de favori (deux champs indépendants : depart / arrivee)."""
    q = q.strip()
    if len(q) < SEUIL_RECHERCHE:
        return templates.TemplateResponse(
            "_favoris_suggestions.html",
            {"request": request, "gares": [], "recherche_faite": False, "champ": champ},
        )

    try:
        gares = client.search_station(q)
    except NavitiaAPIError:
        gares = []

    return templates.TemplateResponse(
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
    favoris = charger_favoris()
    favoris.append(
        Trajet(
            nom=nom.strip(),
            gare_depart_id=gare_depart_id,
            gare_depart_nom=gare_depart_nom,
            gare_arrivee_id=gare_arrivee_id,
            gare_arrivee_nom=gare_arrivee_nom,
        )
    )
    sauvegarder_favoris(favoris)
    return templates.TemplateResponse(
        "_favoris_liste.html",
        {"request": request, "favoris": _construire_contexte_favoris()},
    )


@app.post("/favoris/{index}/toggle", response_class=HTMLResponse)
def toggle_favori(request: Request, index: int):
    favoris = charger_favoris()
    if 0 <= index < len(favoris):
        favoris[index].actif = not favoris[index].actif
        sauvegarder_favoris(favoris)
    return templates.TemplateResponse(
        "_favoris_liste.html",
        {"request": request, "favoris": _construire_contexte_favoris()},
    )


@app.delete("/favoris/{index}", response_class=HTMLResponse)
def supprimer_favori(request: Request, index: int):
    favoris = charger_favoris()
    if 0 <= index < len(favoris):
        favoris.pop(index)
        sauvegarder_favoris(favoris)
    return templates.TemplateResponse(
        "_favoris_liste.html",
        {"request": request, "favoris": _construire_contexte_favoris()},
    )


@app.post("/favoris/{index}/retour", response_class=HTMLResponse)
def creer_trajet_retour(request: Request, index: int):
    favoris = charger_favoris()
    if 0 <= index < len(favoris):
        trajet = favoris[index]
        favoris.append(
            Trajet(
                nom=f"{trajet.nom} (retour)",
                gare_depart_id=trajet.gare_arrivee_id,
                gare_depart_nom=trajet.gare_arrivee_nom,
                gare_arrivee_id=trajet.gare_depart_id,
                gare_arrivee_nom=trajet.gare_depart_nom,
            )
        )
        sauvegarder_favoris(favoris)
    return templates.TemplateResponse(
        "_favoris_liste.html",
        {"request": request, "favoris": _construire_contexte_favoris()},
    )


# --- Statistiques --------------------------------------------------------

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


def _figure_vers_png(fig) -> Response:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110, transparent=True)
    plt.close(fig)
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")


@app.get("/stats", response_class=HTMLResponse)
def page_stats(request: Request):
    contexte = {"request": request, "page": "stats"}

    try:
        df = charger_donnees()
    except FileNotFoundError as err:
        contexte["message_vide"] = str(err)
        return templates.TemplateResponse("stats.html", contexte)

    stats_ligne = stats_ponctualite_par_ligne(df)
    if stats_ligne.empty:
        contexte["message_vide"] = "Pas encore assez de données collectées pour afficher des statistiques."
        return templates.TemplateResponse("stats.html", contexte)

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
    return templates.TemplateResponse("stats.html", contexte)


@app.get("/stats/graphique/retard-ligne.png")
def graphique_retard_ligne():
    df = charger_donnees()
    stats = stats_ponctualite_par_ligne(df)
    return _figure_vers_png(graphe_retard_par_ligne(stats))


@app.get("/stats/graphique/tendance.png")
def graphique_tendance():
    df = charger_donnees()
    tendance = tendance_retard_dans_le_temps(df)
    return _figure_vers_png(graphe_tendance_temporelle(tendance))


@app.get("/stats/graphique/heatmap.png")
def graphique_heatmap():
    df = charger_donnees()
    pivot = heatmap_retards_heure_jour(df)
    return _figure_vers_png(graphe_heatmap_retards(pivot))


@app.get("/stats/export/csv")
def export_stats_csv():
    df = charger_donnees()
    stats_affichage = formater_stats_affichage(stats_ponctualite_par_ligne(df))
    csv_bytes = stats_affichage.to_csv().encode("utf-8")
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=traincker_stats.csv"},
    )


@app.get("/stats/export/pdf")
def export_stats_pdf():
    df = charger_donnees()
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
