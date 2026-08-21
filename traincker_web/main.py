"""
Prototype FastAPI + HTMX pour Traincker.

Étape 1 de la migration : recherche de gare + affichage des prochains
départs. Ne touche à rien côté Streamlit (dashboard.py) — coexistence
totale pendant la migration.

Lancer en local :
    uvicorn traincker_web.main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from traincker.api_client import NavitiaClient, NavitiaAPIError
from traincker.utils import formater_heure, calculer_compte_a_rebours
from traincker.favoris import charger_favoris, sauvegarder_favoris
from traincker.models import Trajet
from traincker.icons import icono, titre_section

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
