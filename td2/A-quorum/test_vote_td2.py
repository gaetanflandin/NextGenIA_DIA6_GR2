import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

from vote_td2 import DATA, Orchestrateur, rejouer, selectionner_proposition


DOSSIER = Path(__file__).resolve().parent


def proposition(modele, valeur, verdict="executed", fournisseur="groq"):
    return {
        "provider": fournisseur,
        "model_requested": modele,
        "value": valeur,
        "verdict": verdict,
    }


class TestVote(unittest.TestCase):
    def setUp(self):
        self.vote = Orchestrateur().vote_k_sur_n

    def test_accord_retourne_toutes_les_voix(self):
        traces = [proposition(modele, 42) for modele in ("a", "b", "c")]
        self.assertEqual(self.vote(traces, 2), {
            "consensus": True, "value": 42, "votes": 3,
            "models": ["groq:a", "groq:b", "groq:c"],
        })

    def test_desaccord_retourne_le_plus_grand_accord(self):
        traces = [proposition(modele, valeur) for modele, valeur in zip("abcde", [1, 1, 2, 2, 3])]
        self.assertEqual(self.vote(traces, 3), {
            "consensus": False, "value": None, "votes": 2, "models": [],
        })

    def test_indisponibilites_ne_reduisent_pas_le_panel(self):
        traces = [
            proposition("a", 42), proposition("b", 42),
            proposition("c", 42, "error"),
            proposition("d", None, "error"),
            proposition("e", None),
        ]
        self.assertEqual(self.vote(traces, 3), {
            "consensus": False, "value": None, "votes": 2, "models": [],
        })

    def test_aucune_voix_exploitable(self):
        traces = [proposition("a", None), proposition("b", "0"), proposition("c", False)]
        self.assertEqual(self.vote(traces, 2), {
            "consensus": False, "value": None, "votes": 0, "models": [],
        })

    def test_vote_pour_zero(self):
        traces = [proposition("a", 0), proposition("b", 0), proposition("c", 9)]
        self.assertEqual(self.vote(traces, 2), {
            "consensus": True, "value": 0, "votes": 2, "models": ["groq:a", "groq:b"],
        })

    def test_doublon_meme_si_indisponible(self):
        traces = [proposition("a", 0), proposition("b", 0), proposition("a", None, "error")]
        with self.assertRaises(ValueError):
            self.vote(traces, 2)

    def test_meme_nom_chez_deux_fournisseurs(self):
        traces = [proposition("a", 42), proposition("a", 42, fournisseur="openrouter")]
        self.assertEqual(self.vote(traces, 2), {
            "consensus": True, "value": 42, "votes": 2, "models": ["groq:a", "openrouter:a"],
        })

    def test_seuils_invalides(self):
        traces = [proposition(modele, 42) for modele in "abcd"]
        for seuil in (-1, 0, 1, 2, 5, 3.0, True):
            with self.subTest(seuil=seuil), self.assertRaises(ValueError):
                self.vote(traces, seuil)

    def test_panel_vide(self):
        with self.assertRaises(ValueError):
            self.vote([], 1)


class TestPolicySynthetique(unittest.TestCase):
    """Les réponses multiples et les latences limites sont synthétiques."""

    def selection(self, *reponses, modele="a"):
        return selectionner_proposition(("groq", modele), reponses)

    def test_9999_ms(self):
        self.assertEqual(self.selection(dict(value=0, verdict="executed", latency_ms=9999))["value"], 0)

    def test_10000_ms(self):
        self.assertEqual(self.selection(dict(value=42, verdict="executed", latency_ms=10000))["value"], 42)

    def test_10001_ms(self):
        self.assertEqual(self.selection(dict(value=42, verdict="executed", latency_ms=10001)),
                         proposition("a", None, "error"))

    def test_timeout_majorite_conservee(self):
        traces = [
            self.selection(dict(value=42, verdict="executed", latency_ms=latence), modele=modele)
            for modele, latence in zip("abc", (9999, 10000, 10001))
        ]
        self.assertEqual(Orchestrateur().vote_k_sur_n(traces, 2), {
            "consensus": True, "value": 42, "votes": 2, "models": ["groq:a", "groq:b"],
        })

    def test_timeout_entraine_abstention(self):
        traces = [
            self.selection(dict(value=valeur, verdict="executed", latency_ms=latence), modele=modele)
            for modele, valeur, latence in zip("abc", (42, 42, 17), (9999, 10001, 9999))
        ]
        self.assertEqual(Orchestrateur().vote_k_sur_n(traces, 2), {
            "consensus": False, "value": None, "votes": 1, "models": [],
        })

    def test_correction_explicite(self):
        premiere = dict(value=42, verdict="executed", latency_ms=5000, role="finale")
        correction = dict(value=17, verdict="executed", latency_ms=10000, role="correction")
        self.assertEqual(self.selection(premiere, correction), proposition("a", 17))

    def test_finale_identifiable_meme_si_premiere(self):
        finale = dict(value=42, verdict="executed", latency_ms=5000, role="finale")
        autre = dict(value=17, verdict="executed", latency_ms=6000)
        self.assertEqual(self.selection(finale, autre), proposition("a", 42))

    def test_contradiction_ambigue(self):
        premiere = dict(value=42, verdict="executed", latency_ms=5000)
        seconde = dict(value=17, verdict="executed", latency_ms=6000)
        self.assertEqual(self.selection(premiere, seconde), proposition("a", None, "error"))

    def test_correction_hors_delai_ignoree(self):
        premiere = dict(value=42, verdict="executed", latency_ms=5000)
        correction = dict(value=17, verdict="executed", latency_ms=10001, role="correction")
        self.assertEqual(self.selection(premiere, correction), proposition("a", 42))

    def test_correction_sql_invalide(self):
        premiere = dict(value=42, verdict="executed", latency_ms=5000)
        correction = dict(value=None, verdict="error", latency_ms=6000, role="correction")
        self.assertEqual(self.selection(premiere, correction), proposition("a", None, "error"))

    def test_absence_et_erreur_sql_ne_votent_pas(self):
        self.assertEqual(self.selection(), proposition("a", None, "error"))
        erreur = dict(value=42, verdict="error", latency_ms=1000)
        self.assertEqual(self.selection(erreur), proposition("a", None, "error"))

    def test_absence_de_double_vote(self):
        reponse = dict(value=42, verdict="executed", latency_ms=5000)
        traces = [self.selection(reponse, reponse), proposition("b", 17), proposition("c", 3)]
        self.assertEqual(Orchestrateur().vote_k_sur_n(traces, 2), {
            "consensus": False, "value": None, "votes": 1, "models": [],
        })


class TestRejeu(unittest.TestCase):
    def test_consensus_errone_sur_les_traces_td1(self):
        resultats = {ligne["case_id"]: ligne for ligne in rejouer(DATA)}
        for cas, valeur in (("C09", 0), ("C10", 119410)):
            with self.subTest(cas=cas):
                ligne = resultats[cas]
                self.assertEqual(ligne["2_sur_3_valeur_cents"], valeur)
                self.assertNotEqual(valeur, ligne["reference_cents"])
                self.assertEqual(ligne["2_sur_3_statut"], "incorrect")
                self.assertEqual(ligne["3_sur_5_statut"], "abstention")

    def test_bilan_des_vingt_questions(self):
        resultats = list(rejouer(DATA))
        self.assertEqual([r["case_id"] for r in resultats], [f"C{i:02}" for i in range(1, 21)])
        self.assertEqual(Counter(r["2_sur_3_statut"] for r in resultats), {
            "correct": 16, "incorrect": 2, "abstention": 2,
        })
        self.assertEqual(Counter(r["3_sur_5_statut"] for r in resultats), {
            "correct": 15, "abstention": 5,
        })

    def test_aide_sans_csv(self):
        resultat = subprocess.run(
            [sys.executable, str(DOSSIER / "vote_td2.py"), "--help"],
            capture_output=True, text=True, check=True,
        )
        self.assertIn("usage:", resultat.stdout)
        self.assertIn("--help", resultat.stdout)
        self.assertNotIn("case_id,reference_cents", resultat.stdout)
        self.assertEqual(resultat.stderr, "")

    def test_csv_identique_au_livrable(self):
        resultat = subprocess.run(
            [sys.executable, str(DOSSIER / "vote_td2.py")],
            capture_output=True, check=True,
        )
        self.assertEqual(resultat.stdout, (DOSSIER / "comparaison-votes.csv").read_bytes())
        self.assertEqual(resultat.stderr, b"")
