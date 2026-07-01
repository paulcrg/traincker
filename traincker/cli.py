"""Interface en ligne de commande pour Traincker."""

import argparse
import sys

from traincker.api_client import NavitiaClient, NavitiaAPIError


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
