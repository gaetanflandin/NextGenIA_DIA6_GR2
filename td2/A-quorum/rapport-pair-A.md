## Pair A — Vote k-of-n

### Objectif et méthode

Nous avons implémenté et comparé deux règles de majorité stricte pour agréger les montants proposés par les modèles sur les 20 questions SQL du TD1. Le rejeu hors ligne utilise les 100 observations de `traces-td1.csv`, une par modèle et par question. Les résultats par question sont disponibles dans `td2/A-quorum/comparaison-votes.csv`.

Pour chaque question, `Orchestrateur.vote_k_sur_n` compte les accords exacts sur les valeurs entières en centimes, y compris zéro. Une réponse exécutée peut voter même si sa valeur se révèle erronée. Une proposition indisponible ne donne aucune voix et reste comptée dans la taille du panel. Le seuil doit satisfaire `n // 2 < k <= n` et les doublons de couples fournisseur-modèle sont rejetés. Si une valeur atteint le seuil, la méthode renvoie cette valeur, le nombre de voix et les modèles qui la soutiennent. Sinon, elle s’abstient et indique la taille du plus grand accord. La référence indépendante, `reference-td1.csv`, sert à évaluer la décision après le vote.

### Timeout et réponses multiples

Le rejeu applique un timeout de **10 000 ms par modèle**, avec une limite inclusive. Une réponse absente, hors délai ou dont le SQL est invalide ne vote pas. La taille du panel et la majorité exigée restent fixes. Le filtrage utilise les latences historiques `latency_ms` et simule les timeouts sans interrompre de véritables appels réseau.

La latence maximale des 100 traces est de **6 928,70 ms**. À 5 s, quatre réponses dépassent le délai, dont une déjà exclue du vote par une erreur SQL. Le 2-sur-3 perd une décision correcte sur C16 et sa couverture passe de 18/20 à 17/20. Le 3-sur-5 perd une décision correcte sur C02 et sa couverture passe de 15/20 à 14/20. Les seuils de 10, 15, 20 et 30 s conservent toutes les décisions historiques. Nous avons retenu le plus court de ces seuils. Les 20 mesures par modèle ne permettent pas de prévoir la fréquence des futurs dépassements.

Chaque modèle fournit au plus une voix. Une réponse explicitement désignée finale est prioritaire. Une correction explicite reçue dans le délai remplace les réponses antérieures et doit être valide pour voter. Une correction tardive est ignorée, ce qui permet à la réponse antérieure de rester admissible. Si les réponses encore en lice se contredisent sans résolution explicite, le modèle est indisponible. Des propositions identiques ne donnent qu’une voix. Les 100 traces distinctes question-modèle, toutes avec `attempts=1`, ne documentent aucun cas réel de réponses multiples. Cette règle est vérifiée à partir de cas synthétiques et suppose que les marqueurs de réponse finale ou de correction soient fournis en amont.

### Panels officiels

| Fournisseur | Modèle | 2-sur-3 | 3-sur-5 |
|---|---|:---:|:---:|
| Groq | `openai/gpt-oss-120b` | Oui | Oui |
| OpenRouter | `cohere/north-mini-code:free` | Oui | Oui |
| Groq | `qwen/qwen3.8-27b` | Oui | Oui |
| Groq | `openai/gpt-oss-20b` | | Oui |
| OpenRouter | `dots-studio/dots-3-note-preview:free` | | Oui |

### Résultats sur les 20 questions

La couverture rapporte le nombre de décisions émises aux 20 questions. L’exactitude parmi les décisions rapporte les décisions correctes aux décisions émises. La part de bonnes décisions sur l’ensemble des questions garde les abstentions au dénominateur.

| Vote | Correctes | Erronées | Abstentions | Couverture | Exactitude parmi les décisions | Bonnes décisions sur l’ensemble |
|---|---:|---:|---:|---:|---:|---:|
| 2-sur-3 | 16 | 2 | 2 | 18/20 (90 %) | 16/18 (88,9 %) | 16/20 (80 %) |
| 3-sur-5 | 15 | 0 | 5 | 15/20 (75 %) | 15/15 (100 %) | 15/20 (75 %) |

| Modèle seul au TD1 | Réponses correctes | Valeurs erronées | SQL invalides |
|---|---:|---:|---:|
| GPT-OSS-120B | 19/20 (95 %) | 1 | 0 |
| Cohere North Mini Code | 13/20 (65 %) | 6 | 1 |
| Qwen 3.8 27B | 14/20 (70 %) | 6 | 0 |
| GPT-OSS-20B | 18/20 (90 %) | 2 | 0 |
| Dots 3 Note Preview | 12/20 (60 %) | 6 | 2 |

Les deux votes s’abstiennent sur C17 et C19. Le 3-sur-5 s’abstient également sur C08, C09 et C10. Sur C08, GPT-OSS-120B et Qwen s’accordent sur la valeur correcte de 605 580 centimes, suffisante pour le 2-sur-3. Les trois propositions indisponibles pour le vote proviennent de SQL invalides, sur C02 pour Cohere et sur C11 et C19 pour Dots.

### Consensus erronés sur C09 et C10

| Question | Référence en centimes | Valeur acceptée par le 2-sur-3 | Modèles d’accord | Décision du 3-sur-5 |
|---|---:|---:|---|---|
| C09 | 487 980 | 0 | Cohere et Qwen | Abstention |
| C10 | 558 980 | 119 410 | Cohere et Qwen | Abstention |

Le 2-sur-3 accepte ces valeurs parce qu’elles atteignent le quorum. Dans les deux cas, GPT-OSS-120B et GPT-OSS-20B donnent la référence, ce qui conduit à deux voix pour la bonne valeur et deux voix pour la mauvaise dans le panel de cinq. La cinquième voix, celle de Dots, porte sur une troisième valeur. Aucune valeur ne recueille trois voix, donc le 3-sur-5 s’abstient. Ces deux cas montrent qu’un accord peut porter sur une erreur partagée. Le rejeu établit l’accord sur les montants, tandis que la cause commune des erreurs SQL reste à établir.

### Limites et enseignements

Sur ce lot, le 2-sur-3 rend trois décisions de plus, dont une correcte et deux erronées. Le 3-sur-5 atteint 100 % d’exactitude parmi ses 15 décisions et laisse cinq questions sans réponse. GPT-OSS-120B seul obtient davantage de réponses correctes sur l’ensemble des 20 questions que chacun des deux votes, avec une erreur.

Le panel et le seuil varient ensemble, ce qui empêche d’attribuer les écarts au seul seuil. Les 20 questions historiques ne permettent pas d’estimer la performance sur de nouvelles questions ni la disponibilité actuelle des modèles. La comparaison met en évidence l’intérêt de publier conjointement l’exactitude et la couverture, et de conserver les valeurs et les modèles qui soutiennent chaque décision pour pouvoir examiner les erreurs.

### Vérification et reproduction

La suite `unittest` couvre le contrat de vote, les deux consensus erronés, le bilan des 20 questions, l’aide et la reproduction du CSV octet pour octet. Les tests synthétiques vérifient les limites de 9 999, 10 000 et 10 001 ms, l’effet d’un timeout sur le quorum, la sélection des réponses multiples et l’absence de double vote. Le rejeu et les tests s’exécutent avec la bibliothèque standard et les fichiers locaux.

Le rejeu et les tests utilisent les fichiers communs `traces-td1.csv` et `reference-td1.csv` à la racine du dépôt. Les traces contiennent 100 enregistrements de données sur 774 lignes physiques, en-tête compris, en raison du SQL multiligne. Depuis la racine, ces commandes affichent l’aide, produisent les résultats, comparent leur sortie au CSV livré et lancent les tests.

```sh
python3.13 td2/A-quorum/vote_td2.py --help
python3.13 td2/A-quorum/vote_td2.py
python3.13 td2/A-quorum/vote_td2.py | cmp - td2/A-quorum/comparaison-votes.csv
python3.13 -B -m unittest discover -s td2/A-quorum -p test_vote_td2.py -v
```
