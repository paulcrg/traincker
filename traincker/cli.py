"""Interface en ligne de commande pour Traincker."""

import argparse
import sys

from traincker.api_client import NavitiaClient, NavitiaAPIError
from traincker.monitor import lancer_surveillance

def cmd_recherche(args):
    """Recherche l'identifiant stop_area d'une gare (à mettre dans favoris.json)."""
    client = NavitiaClient()
    stations = client.search_station(args.gare, count=args.count)

    if not stations:
        print(f"Aucune gare trouvée pour « {args.gare} »")
        sys.exit(1)

    print(f"Résultats pour « {args.gare} » :\n")
    for s in stations:
        print(f"- {s['name']}")
        print(f"  id: {s['id']}\n")


def cmd_surveiller(args):
    """Lance la boucle de surveillance des trajets favoris (bloquant)."""
    lancer_surveillance(intervalle_minutes=args.intervalle)

def cmd_gare(args):
    """Affiche les prochains départs pour une gare recherchée par nom."""
    client = NavitiaClient()

    stations = client.search_station(args.gare)
    if not stations:
        print(f"Aucune gare trouvée pour « {args.gare} »")
        sys.exit(1)

    station = stations[0]
    print(f"Gare sélectionnée : {station['name']}\n")

    departs = client.get_next_departures(station["id"], count=args.count)
    if not departs:
        print("Aucun départ trouvé pour le moment.")
        return

    for d in departs:
        statut = "⏱️ temps réel" if d["statut"] == "realtime" else "📅 théorique"
        print(f"[{statut}] {d['ligne']} → {d['direction']} à {d['heure_prevue']}")


def cmd_perturbations(args):
    """Affiche les perturbations en cours pour une gare."""
    client = NavitiaClient()

    stations = client.search_station(args.gare)
    if not stations:
        print(f"Aucune gare trouvée pour « {args.gare} »")
        sys.exit(1)

    station = stations[0]
    disruptions = client.get_disruptions(station["id"])

    if not disruptions:
        print(f"Aucune perturbation signalée pour {station['name']}. ✅")
        return

    print(f"Perturbations pour {station['name']} :\n")
    for p in disruptions:
        print(f"- {p['titre']} : {p['message']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="traincker",
        description="Suivi des trains SNCF au quotidien.",
    )
    subparsers = parser.add_subparsers(dest="commande", required=True)

    parser_gare = subparsers.add_parser("gare", help="Prochains départs d'une gare")
    parser_gare.add_argument("--gare", required=True, help="Nom de la gare (ex: Dijon)")
    parser_gare.add_argument("--count", type=int, default=10, help="Nombre de départs")
    parser_gare.set_defaults(func=cmd_gare)

    parser_perturb = subparsers.add_parser(
        "perturbations", help="Perturbations en cours pour une gare"
    )
    parser_perturb.add_argument("--gare", required=True, help="Nom de la gare")
    parser_perturb.set_defaults(func=cmd_perturbations)
    parser_recherche = subparsers.add_parser(
        "recherche", help="Chercher l'identifiant (stop_area_id) d'une gare"
    )
    parser_recherche.add_argument("--gare", required=True, help="Nom de la gare à chercher")
    parser_recherche.add_argument("--count", type=int, default=5, help="Nombre de résultats")
    parser_recherche.set_defaults(func=cmd_recherche)

    parser_surveiller = subparsers.add_parser(
        "surveiller", help="Surveille les trajets favoris en continu"
    )
    parser_surveiller.add_argument(
        "--intervalle", type=int, default=5, help="Minutes entre deux vérifications"
    )
    parser_surveiller.set_defaults(func=cmd_surveiller)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        args.func(args)
    except NavitiaAPIError as e:
        print(f"Erreur API : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
