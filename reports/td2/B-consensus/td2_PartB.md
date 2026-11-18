## Étape 2 : faux consensus (Pair B)

**Cas :** C10 (cas de notre batch TD 1, non rejoué).
Question : revenu hors TVA des commandes passées par des clients ayant exactement 25 ans au moment de la commande.

### 1. Identification et verdict des quorums

| Modèle | Valeur (cts) | Verdict |
|---|---|---|
| openai/gpt-oss-120b | 558 980 | correct |
| openai/gpt-oss-20b | 558 980 | correct |
| cohere/north-mini-code:free | 119 410 | incorrect |
| qwen/qwen3.8-27b | 119 410 | incorrect |
| dots-3-note-preview:free | 0 | incorrect |

Référence (`reference-td1.csv`) : **558 980**. Valeur fausse partagée : **119 410** (cohere et qwen).

- Panel 2-sur-3 (gpt-oss-120b, cohere, qwen), k=2 : 119 410 obtient 2 voix, 558 980 une seule. **Le faux consensus gagne.**
- Quorum 3-sur-5, k=3 : 558 980 a 2 voix, 119 410 en a 2, 0 en a 1. Aucune valeur n'atteint 3, donc **abstention**, sans valeur inventée.

### 2. Diagnostic de la clause SQL fautive

L'âge révolu correct est `année_commande - année_naissance - (MM-JJ commande < MM-JJ naissance)`.

- **cohere** : `différence_années = 25 AND MM-JJ(commande) >= MM-JJ(naissance)`. Un client de 25 ans dont l'anniversaire n'est pas encore passé a une différence d'années de 26, donc il est exclu.
- **qwen** : la première branche est correcte, mais la seconde teste `différence = 24` au lieu de `26`. Elle ne rattrape donc pas ces clients.

Les deux requêtes, textuellement différentes, ratent les mêmes lignes. Les erreurs sont corrélées.

(Requêtes complètes : voir `traces-td1.csv`, lignes C10.)

### 3. Requête delta (exécutée sur `data/boutique.sqlite`)

Script : `delta_c10.py`. Il liste les clients de 25 ans (âge révolu) dont la différence d'années vaut 26.

| customer_id | lignes | revenu manqué (cts) |
|---|---|---|
| C004 | 17 | 150 260 |
| C005 | 20 | 150 240 |
| C007 | 18 | 118 740 |
| C022 | 4 | 20 330 |
| **Total** | 59 | **439 570** |

Contrôle : 558 980 − 119 410 = 439 570. L'écart est entièrement expliqué.

### Conséquence pour le contrôle

Un vote majoritaire ne protège pas contre des erreurs corrélées : deux modèles peuvent se tromper de la même manière. Pour une donnée sensible, il faut un contrôle déterministe contre une référence, ou une abstention quand le quorum n'est pas atteint.