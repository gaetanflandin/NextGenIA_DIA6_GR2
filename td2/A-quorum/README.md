# TD2 — Pair A · Vote k-of-n

Le script rejoue les décisions sur les vingt questions du TD1 avec Python 3 et sa bibliothèque standard. Les deux CSV communs doivent être présents à la racine du dépôt. Depuis cette racine, ces commandes affichent l’aide, produisent le CSV et vérifient que le résultat correspond au fichier livré.

```sh
python3.13 td2/A-quorum/vote_td2.py --help
python3.13 td2/A-quorum/vote_td2.py
python3.13 td2/A-quorum/vote_td2.py | cmp - td2/A-quorum/comparaison-votes.csv
```

Pour lancer les tests du contrat, du rejeu et de l’interface en ligne de commande, utilise la commande suivante. La suite s’exécute hors ligne avec les fichiers du dépôt et la bibliothèque standard.

```sh
python3.13 -B -m unittest discover -s td2/A-quorum -p test_vote_td2.py -v
```

Le fichier [comparaison-votes.csv](comparaison-votes.csv) conserve les résultats du rejeu. Les entrées sont les [traces du TD1](../../traces-td1.csv) et la [référence indépendante](../../reference-td1.csv). Le fichier de traces contient 100 enregistrements de données répartis sur 774 lignes physiques, en-tête compris, car le champ SQL contient des retours à la ligne. Les [prompts documentés au TD1](../../contributions/hela/model-D/prompts-en.md) restent disponibles dans la contribution d’origine.

## Protocole

Le 2-sur-3 utilise GPT-OSS-120B et Qwen 3.8 27B via Groq, et Cohere North Mini Code via OpenRouter. Le 3-sur-5 ajoute GPT-OSS-20B via Groq et Dots 3 Note Preview via OpenRouter. Chaque membre reste dans le panel, y compris en cas d’indisponibilité.

Les verdicts TD1 correct et incorrect avec une valeur en centimes deviennent des propositions exécutées. Les SQL invalides deviennent des erreurs sans voix. Les valeurs sont comparées exactement, y compris zéro. Une majorité stricte est obligatoire et tout doublon fournisseur-modèle dans une question est rejeté. Sans quorum, le résultat contient la taille du plus grand accord, une valeur vide et une liste de modèles vide. La référence sert uniquement à évaluer la décision après le vote.

### Timeout et réponses multiples

Le rejeu applique un timeout de **10 000 ms par modèle** à partir de `latency_ms`. La limite est inclusive. Une réponse absente, hors délai ou dont le SQL est invalide ne donne aucune voix. Le membre reste dans le panel et le seuil de majorité reste fixe. Le rejeu est hors ligne et simule l’indisponibilité après coup. L’interruption réelle des appels réseau ne fait pas partie de cette implémentation.

La latence maximale des 100 traces est de **6 928,70 ms**. À 5 s, quatre traces dépassent le délai, dont une déjà inutilisable à cause d’un SQL invalide. La couverture passe de 18/20 à 17/20 pour le 2-sur-3 et de 15/20 à 14/20 pour le 3-sur-5. À 10, 15, 20 et 30 s, toutes les décisions historiques sont conservées. Dix secondes est donc le seuil testé le plus court qui préserve ces décisions.

La sélection traite les propositions d’un modèle dans l’ordre de réception et ignore d’abord celles hors délai. Un marqueur explicite `role=finale` donne la priorité à la réponse désignée. Une proposition marquée `role=correction` et arrivée dans le délai remplace les précédentes. Si la correction est invalide, le modèle est indisponible. Une correction tardive est ignorée et la réponse antérieure peut rester admissible. Sans désignation explicite, des valeurs identiques donnent une seule voix et des réponses contradictoires rendent le modèle indisponible. Des désignations finales incompatibles rendent également le modèle indisponible.

Les traces du TD1 ne contiennent qu’un enregistrement par couple question-modèle, tous avec `attempts=1`. Elles ne fournissent pas de marqueur de réponse finale ou de correction. Les cas multiples sont vérifiés par des tests synthétiques. Les marqueurs doivent être fournis après identification explicite de la réponse, car le rejeu ne les déduit pas d’un texte libre.

## Résultats

| Configuration | Correctes sur 20 | Erronées | Abstentions | Couverture | Exactitude parmi les décisions |
|---|---:|---:|---:|---:|---:|
| 2-sur-3 | 16/20 (80 %) | 2 | 2 | 18/20 (90 %) | 16/18 (88,9 %) |
| 3-sur-5 | 15/20 (75 %) | 0 | 5 | 15/20 (75 %) | 15/15 (100 %) |

| Modèle seul | Correctes sur 20 | Erronées | SQL invalides |
|---|---:|---:|---:|
| GPT-OSS-120B | 19 | 1 | 0 |
| Cohere North Mini Code | 13 | 6 | 1 |
| Qwen 3.8 27B | 14 | 6 | 0 |
| GPT-OSS-20B | 18 | 2 | 0 |
| Dots 3 Note Preview | 12 | 6 | 2 |

- Sur C08, GPT-OSS-120B et Qwen donnent la bonne valeur, 605580. Le 2-sur-3 l’accepte et le 3-sur-5 s’abstient.
- Sur C09 et C10, Cohere et Qwen s’accordent respectivement sur 0 et 119410. Le 2-sur-3 accepte ces valeurs erronées. Les références sont 487980 et 558980. Le 3-sur-5 s’abstient dans les deux cas.
- Les deux configurations s’abstiennent sur C17 et C19.
- Trois propositions sont indisponibles pour le vote à cause d’un SQL invalide, Cohere sur C02 et Dots sur C11 et C19. Les 100 traces historiques ont un statut HTTP 200 et chaque couple modèle-question est unique.

Les résultats décrivent un lot historique de 20 questions. La comparaison fait varier ensemble la composition du panel et le seuil. Elle ne mesure ni la disponibilité actuelle ni les performances sur de nouvelles questions.

## Sources et revue

Le contrat de la méthode est documenté dans le [squelette officiel local](../../contributions/hela/model-D/official/skeleton-multi-llm-en.py#L603). L’énoncé TD2, le script atelier-vote.py, le barème et les modalités de remise en ligne étaient inaccessibles. L’intégration directe à l’atelier et les attendus propres à Pair A restent à vérifier. Les comptes rendus de revue pourront être ajoutés après les séances correspondantes.
