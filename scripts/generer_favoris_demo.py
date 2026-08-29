"""
Script à lancer localement (avec une clé SNCF_API_KEY valide) pour
retrouver les stop_area_id des gares des trajets de démonstration, et
générer le JSON à coller dans config/favoris.json.

Usage :
    python scripts/generer_favoris_demo.py

Les trajets internationaux (ex: Zürich HB) ne sont pas garantis d'être
dans la couverture Navitia "sncf" — le script affiche "AUCUN RÉSULTAT"
si une gare n'est pas trouvée ; il faut alors vérifier/adapter le nom
(éventuellement une gare frontière comme "Bâle SNCF"), ou confirmer que
la desserte existe bien dans les données SNCF (ex: TGV Lyria).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from traincker.api_client import NavitiaClient, NavitiaAPIError

TRAJETS_DEMO = [
    ("Dijon-Zurich HB", "Dijon", "Zürich HB"),
    ("Paris-Bruxelles", "Paris Nord", "Bruxelles Midi"),
    ("Dijon-Chalon-sur-Saône", "Dijon", "Chalon-sur-Saône"),
    ("Paris-Bordeaux", "Paris Montparnasse", "Bordeaux Saint-Jean"),
    ("Marseille-Lyon", "Marseille Saint-Charles", "Lyon Part-Dieu"),
    ("Nuits-Saint-Georges-Dijon", "Nuits-Saint-Georges", "Dijon"),
    ("Dijon-Nuits-Saint-Georges", "Dijon", "Nuits-Saint-Georges"),
]


def trouver_gare(client: NavitiaClient, nom: str) -> dict | None:
    """Affiche tous les résultats trouvés (pas seulement le premier) : la
    recherche SNCF peut renvoyer des résultats surprenants sur certaines
    requêtes. Demande confirmation à l'utilisateur, avec la possibilité
    de retaper une autre recherche si rien ne convient."""
    while True:
        try:
            resultats = client.search_station(nom, count=8)
        except NavitiaAPIError as err:
            print(f"  ERREUR API pour « {nom} » : {err}")
            return None

        if resultats:
            print(f"  Résultats pour « {nom} » :")
            for i, r in enumerate(resultats):
                print(f"    [{i}] {r['name']}  ({r['id']})")
        else:
            print(f"  AUCUN RÉSULTAT pour « {nom} »")

        choix = input(
            f"  -> Numéro de la vraie gare [0-{len(resultats) - 1}], "
            "'r' pour retaper une recherche, ou 's' pour passer : "
        ).strip().lower()

        if choix == "s":
            return None
        if choix == "r":
            nom = input("  Nouvelle recherche : ").strip()
            continue
        if choix.isdigit() and 0 <= int(choix) < len(resultats):
            return resultats[int(choix)]
        print("  Choix invalide, réessaie.")


def main():
    client = NavitiaClient()
    trajets_json = []

    for nom_trajet, gare_depart, gare_arrivee in TRAJETS_DEMO:
        print(f"\n{nom_trajet} :")
        depart = trouver_gare(client, gare_depart)
        arrivee = trouver_gare(client, gare_arrivee)

        if depart:
            print(f"  Départ  -> {depart['name']} ({depart['id']})")
        if arrivee:
            print(f"  Arrivée -> {arrivee['name']} ({arrivee['id']})")

        if depart and arrivee:
            trajets_json.append(
                {
                    "nom": nom_trajet,
                    "gare_depart_id": depart["id"],
                    "gare_depart_nom": depart["name"],
                    "gare_arrivee_id": arrivee["id"],
                    "gare_arrivee_nom": arrivee["name"],
                    "actif": True,
                    "cree_le": None,
                }
            )

    print("\n\n--- JSON à coller dans config/favoris.json (clé \"trajets\") ---\n")
    print(json.dumps(trajets_json, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
