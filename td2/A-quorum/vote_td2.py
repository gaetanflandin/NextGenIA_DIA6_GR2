"""Rejoue les votes de Pair A à partir des traces TD1, sans réseau."""

import argparse
import csv
import json
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


DATA = Path(__file__).resolve().parents[2]
TIMEOUT_MS = 10_000
PANEL_3 = (
    ("groq", "openai/gpt-oss-120b"),
    ("openrouter", "cohere/north-mini-code:free"),
    ("groq", "qwen/qwen3.8-27b"),
)
PANEL_5 = PANEL_3 + (
    ("groq", "openai/gpt-oss-20b"),
    ("openrouter", "dots-studio/dots-3-note-preview:free"),
)


class Orchestrateur:
    def vote_k_sur_n(self, traces_question: list, k: int) -> dict:
        """Compte les valeurs exécutées pour un panel et un seuil fixes."""
        n = len(traces_question)
        if type(k) is not int or not n // 2 < k <= n:
            raise ValueError(f"k doit être une majorité stricte pour n={n}")

        membres = set()
        voix = defaultdict(list)
        for trace in traces_question:
            membre = (trace["provider"], trace["model_requested"])
            if membre in membres:
                raise ValueError(f"Proposition en double pour {membre}")
            membres.add(membre)
            valeur = trace["value"]
            if trace["verdict"] == "executed" and type(valeur) is int:
                voix[valeur].append(":".join(membre))

        valeur, modeles = max(voix.items(), key=lambda item: len(item[1]), default=(None, []))
        if len(modeles) >= k:
            return {"consensus": True, "value": valeur, "votes": len(modeles), "models": modeles}
        return {"consensus": False, "value": None, "votes": len(modeles), "models": []}


def selectionner_proposition(membre, reponses):
    """Ramène les réponses d'un membre à une proposition du contrat de vote.

    Le rôle facultatif 'finale' ou 'correction' doit venir d'un signal explicite.
    Les réponses sont rangées par ordre de réception. Les latences sont
    mesurées depuis le départ de l'appel du membre.
    """
    dans_le_delai = []
    for reponse in reponses:
        try:
            latence = Decimal(str(reponse.get("latency_ms")))
        except InvalidOperation:
            continue
        if latence.is_finite() and 0 <= latence <= TIMEOUT_MS:
            if reponse.get("role") == "correction":
                dans_le_delai.clear()
            dans_le_delai.append(reponse)

    explicites = [
        r for r in dans_le_delai if r.get("role") in {"finale", "correction"}
    ]
    valeurs = {
        r["value"] if r["verdict"] == "executed" and type(r["value"]) is int else None
        for r in (explicites or dans_le_delai)
    }
    valeur = valeurs.pop() if len(valeurs) == 1 else None
    return {
        "provider": membre[0],
        "model_requested": membre[1],
        "value": valeur,
        "verdict": "executed" if valeur is not None else "error",
    }


def rejouer(data: Path):
    with (data / "reference-td1.csv").open(encoding="utf-8-sig", newline="") as fichier:
        references = {}
        for ligne in csv.DictReader(fichier):
            cas = ligne["case_id"]
            if cas in references:
                raise ValueError(f"Référence en double pour {cas}")
            references[cas] = int(ligne["revenue_cents"])

    traces = defaultdict(lambda: defaultdict(list))
    with (data / "traces-td1.csv").open(encoding="utf-8-sig", newline="") as fichier:
        for ligne in csv.DictReader(fichier):
            cas = ligne["case_id"]
            membre = (ligne["provider"], ligne["model_requested"])
            execute = ligne["verdict"] in {"correct", "incorrect"} and bool(ligne["value"].strip())
            traces[cas][membre].append({
                "value": int(ligne["value"]) if execute else None,
                "verdict": "executed" if execute else "error",
                "latency_ms": ligne["latency_ms"],
                "role": ligne.get("role"),
            })
    if set(traces) - references.keys():
        raise ValueError("Des traces correspondent à des questions sans référence")

    orchestrateur = Orchestrateur()
    for cas, reference in sorted(references.items()):
        propositions = [
            selectionner_proposition(membre, traces[cas].get(membre, ()))
            for membre in PANEL_5
        ]
        resultat = {
            "case_id": cas,
            "reference_cents": reference,
            **{
                ":".join(membre): proposition["value"]
                for membre, proposition in zip(PANEL_5, propositions)
            },
        }
        for label, taille, seuil in (("2_sur_3", len(PANEL_3), 2), ("3_sur_5", len(PANEL_5), 3)):
            vote = orchestrateur.vote_k_sur_n(propositions[:taille], seuil)
            if not vote["consensus"]:
                statut = "abstention"
            else:
                statut = "correct" if vote["value"] == reference else "incorrect"
            resultat.update({
                f"{label}_statut": statut,
                f"{label}_valeur_cents": vote["value"],
                f"{label}_voix": vote["votes"],
                f"{label}_modeles": json.dumps(vote["models"]),
            })
        yield resultat


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    resultats = list(rejouer(DATA))
    if resultats:
        sortie = csv.DictWriter(sys.stdout, fieldnames=list(resultats[0]), lineterminator="\n")
        sortie.writeheader()
        sortie.writerows(resultats)
