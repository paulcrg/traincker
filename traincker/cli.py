"""Interface en ligne de commande pour Traincker."""

import argparse
import sys
from pathlib import Path

from traincker.api_client import NavitiaClient, NavitiaAPIError
from traincker.monitor import lancer_surveillance, verifier_favoris
from traincker.utils import formater_heure


def cmd_recherche(args):
    client = NavitiaClient()
    stations = client.search_station(args.gare, count=args.count)
    if not stations:
        print(f"Aucune gare trouvée pour « {args.gare} »")
        sys.exit(1)
    print(f"Résultats pour « {args.gare} » :\n")
    for s in stations:
        print(f"- {s['name']}\n  id: {s['id']}\n")


def cmd_surveiller(args):
    lancer_surveillance(intervalle_minutes=args.intervalle)


def cmd_verifier(args):
    verifier_favoris()


def cmd_stats(args):
    from traincker.analysis import charger_donnees, stats_ponctualite_par_ligne, tendance_retard_dans_le_temps
    from traincker.viz import graphe_retard_par_ligne, graphe_tendance_temporelle

    try:
        df = charger_donnees()
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)

    if df.empty:
        print("Aucune donnée exploitable pour le moment.")
        return

    stats = stats_ponctualite_par_ligne(df)
    print("\nStatistiques de ponctualité par ligne :\n")
    print(stats)

    dossier_sortie = Path("data/processed")
    graphe_retard_par_ligne(stats, save_path=str(dossier_sortie / "retard_par_ligne.png"))
    tendance = tendance_retard_dans_le_temps(df)
    graphe_tendance_temporelle(tendance, save_path=str(dossier_sortie / "tendance_retard.png"))
    print(f"\nGraphes sauvegardés dans {dossier_sortie}/")


def cmd_gare(args):
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
        statut = "temps réel" if d["statut"] == "realtime" else "théorique"
        print(f"[{statut}] {d['ligne']} → {d['direction']} à {formater_heure(d['heure_prevue'])}")


def cmd_perturbations(args):
    client = NavitiaClient()
    stations = client.search_station(args.gare)
    if not stations:
        print(f"Aucune gare trouvée pour « {args.gare} »")
        sys.exit(1)

    station = stations[0]
    disruptions = client.get_disruptions(station["id"])
    if not disruptions:
        print(f"Aucune perturbation signalée pour {station['name']}.")
        return

    print(f"Perturbations pour {station['name']} :\n")
    for p in disruptions:
        print(f"- {p['titre']} : {p['message']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="traincker", description="Suivi des trains SNCF au quotidien.")
    subparsers = parser.add_subparsers(dest="commande", required=True)

    p_gare = subparsers.add_parser("gare", help="Prochains départs d'une gare")
    p_gare.add_argument("--gare", required=True)
    p_gare.add_argument("--count", type=int, default=10)
    p_gare.set_defaults(func=cmd_gare)

    p_perturb = subparsers.add_parser("perturbations", help="Perturbations en cours pour une gare")
    p_perturb.add_argument("--gare", required=True)
    p_perturb.set_defaults(func=cmd_perturbations)

    p_recherche = subparsers.add_parser("recherche", help="Chercher l'identifiant d'une gare")
    p_recherche.add_argument("--gare", required=True)
    p_recherche.add_argument("--count", type=int, default=5)
    p_recherche.set_defaults(func=cmd_recherche)

    p_surveiller = subparsers.add_parser("surveiller", help="Surveille les trajets favoris en continu")
    p_surveiller.add_argument("--intervalle", type=int, default=5)
    p_surveiller.set_defaults(func=cmd_surveiller)

    p_verifier = subparsers.add_parser("verifier", help="Une seule vérification (pour un cron externe)")
    p_verifier.set_defaults(func=cmd_verifier)

    p_stats = subparsers.add_parser("stats", help="Statistiques de ponctualité et graphes")
    p_stats.set_defaults(func=cmd_stats)

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
