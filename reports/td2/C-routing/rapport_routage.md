## Étape 3 — Règle de routage et simulation (Pair C)

### 3.1 Taux de réussite exact par modèle et par famille (TD 1)

Le calcul sur les 20 traces réelles validées au TD 1 (`model-question-comparison-en.csv`, regroupées selon les 5 familles exclusives du protocole) donne les performances suivantes :

| Modèle | Period (6) | Completed age at a date (4) | Age at the order (1) | Product list (4) | Combinations (5) | Global (20) |
|---|---|---|---|---|---|---|
| `openrouter:cohere/north-mini-code:free` | **6/6** (100 %)<br>_C01, C04, C05, C06, C07, C20_ | **0/4** (0 %)<br>_-_ | **0/1** (0 %)<br>_-_ | **4/4** (100 %)<br>_C03, C12, C13, C14_ | **3/5** (60 %)<br>_C15, C16, C18_ | **13/20 (65 %)** |
| `openrouter:dots-studio/dots-3-note-preview:free` | **6/6** (100 %)<br>_C01, C04, C05, C06, C07, C20_ | **1/4** (25 %)<br>_C02_ | **0/1** (0 %)<br>_-_ | **4/4** (100 %)<br>_C03, C12, C13, C14_ | **1/5** (20 %)<br>_C16_ | **12/20 (60 %)** |
| `groq:openai/gpt-oss-120b` | **6/6** (100 %)<br>_C01, C04, C05, C06, C07, C20_ | **4/4** (100 %)<br>_C02, C08, C09, C11_ | **1/1** (100 %)<br>_C10_ | **4/4** (100 %)<br>_C03, C12, C13, C14_ | **4/5** (80 %)<br>_C15, C16, C17, C18_ | **19/20 (95 %)** |
| `groq:openai/gpt-oss-20b` | **6/6** (100 %)<br>_C01, C04, C05, C06, C07, C20_ | **2/4** (50 %)<br>_C09, C11_ | **1/1** (100 %)<br>_C10_ | **4/4** (100 %)<br>_C03, C12, C13, C14_ | **5/5** (100 %)<br>_C15, C16, C17, C18, C19_ | **18/20 (90 %)** |
| `groq:qwen/qwen3.8-27b` | **6/6** (100 %)<br>_C01, C04, C05, C06, C07, C20_ | **3/4** (75 %)<br>_C02, C08, C11_ | **0/1** (0 %)<br>_-_ | **4/4** (100 %)<br>_C03, C12, C13, C14_ | **1/5** (20 %)<br>_C18_ | **14/20 (70 %)** |

**Limites de validité :** Ces résultats constituent une hypothèse de routage propre à ce lot de 20 questions (température 0, une tentative par cellule), et non un classement général ou une garantie d'absence d'erreur.

---

### 3.2 Règle de routage du sous-groupe

Pour chaque famille, le routeur sélectionne le modèle le moins cher du portefeuille ayant atteint 100 % de réussite sur cette famille au TD 1, applique un contrôle proportionnel au coût d'erreur de l'usage, et refuse tout repli vers un modèle non fiable.

| Famille de questions | 1er modèle appelé | Justification (cellules TD 1 & portefeuille) | Vérification selon l'usage | Conduite si indisponible |
|---|---|---|---|---|
| **Period** | `openrouter:cohere/north-mini-code:free` (route `:free`, $0) | 6/6 (100 %) sur `C01, C04, C05, C06, C07, C20` | • *Dashboard interne* : exécution read-only<br>• *Affiché client* : quorum 2-sur-3 (`cohere` + `dots` + `gpt-oss-20b`)<br>• *Montant versé* : quorum 2-sur-3 + requête de référence / revue humaine | Repli vers `openrouter:dots-studio/dots-3-note-preview:free` (6/6), puis `groq:openai/gpt-oss-20b` (6/6). Si tous épuisés : `defer` jusqu'au reset si non urgent, sinon `abstain`. |
| **Product list** | `openrouter:cohere/north-mini-code:free` (route `:free`, $0) | 4/4 (100 %) sur `C03, C12, C13, C14` | • *Dashboard interne* : exécution read-only<br>• *Affiché client* : quorum 2-sur-3 (`cohere` + `dots` + `gpt-oss-20b`)<br>• *Montant versé* : quorum 2-sur-3 + requête de référence / revue humaine | Repli vers `openrouter:dots-studio/dots-3-note-preview:free` (4/4), puis `groq:openai/gpt-oss-20b` (4/4). Si tous épuisés : `defer` si non urgent, sinon `abstain`. |
| **Age at the order** | `groq:openai/gpt-oss-20b` (Groq Free puis Developer $0.075/$0.30 par 1M) | 1/1 (100 %) sur `C10` (0 % pour Cohere, Dots et Qwen) | • *Dashboard interne* : contrôle des bornes SQL d'âge<br>• *Affiché client* : assertion SQL / requête de référence (quorum 2-sur-3 écarté car Cohere et Qwen font un faux consensus sur `C10`)<br>• *Montant versé* : revue humaine obligatoire | Repli vers `groq:openai/gpt-oss-120b` (1/1 sur `C10`, $0.15/$0.60 par 1M). Si quotas Groq épuisés : `defer` si différable, sinon `abstain` (Cohere, Dots et Qwen interdits). |
| **Completed age at a date** | `groq:openai/gpt-oss-120b` (Groq Free puis Developer $0.15/$0.60 par 1M) | 4/4 (100 %) sur `C02, C08, C09, C11` (seul modèle à 100 % sur cette famille) | • *Dashboard interne* : contrôle des bornes SQL de date<br>• *Affiché client* : vérification déterministe des bornes de date (quorum 2-sur-3 écarté suite au faux consensus Cohere/Qwen sur `C09`)<br>• *Montant versé* : revue humaine obligatoire | Aucun autre modèle n'atteint 100 % (`qwen` 3/4, `gpt-oss-20b` 2/4) : basculer vers la route payante Groq Developer (`gpt-oss-120b`), `defer` si différable et budget nul, sinon `abstain`. |
| **Combinations** | `groq:openai/gpt-oss-20b` (Groq Free puis Developer $0.075/$0.30 par 1M) | 5/5 (100 %) sur `C15, C16, C17, C18, C19` | • *Dashboard interne* : exécution read-only + contrôle de non-nullité<br>• *Affiché client* : double exécution `gpt-oss-20b` + `gpt-oss-120b` (4/5 sur `C15–C18`) avec arbitrage si désaccord<br>• *Montant versé* : double exécution + revue humaine obligatoire | Repli vers `groq:openai/gpt-oss-120b` (4/5 sur `C15–C18`, alerte revue sur cumul de 3 filtres comme `C19`). Si indisponibles : `defer` si différable, sinon `abstain` (Cohere 3/5, Dots 1/5, Qwen 1/5 exclus). |

---

### 3.3 Sorties du simulateur (`atelier-routage.py`) avant et après adaptation

#### Avant adaptation (ressources fictives du squelette)
```{json}
{"scenario": "simple", "nature": "simulation", "request": {"difficulty": 1, "high_impact": false, "can_wait": true, "deadline_minutes": 120, "budget": 0.3}, "result": {"action": "run", "resource": "small-free", "cash": 0, "checks": "read-only execution and value check", "reason": "eligible included capacity"}}
{"scenario": "complex", "nature": "simulation", "request": {"difficulty": 3, "high_impact": false, "can_wait": true, "deadline_minutes": 120, "budget": 0.3}, "result": {"action": "run", "resource": "senior-subscription", "cash": 0, "checks": "read-only execution and value check", "reason": "eligible included capacity"}}
{"scenario": "deferrable", "nature": "simulation", "request": {"difficulty": 3, "high_impact": false, "can_wait": true, "deadline_minutes": 120, "budget": 0.3}, "result": {"action": "defer", "resource": "senior-subscription", "cash": 0, "checks": "read-only execution and value check", "reason": "recheck availability at wake-up", "wake_in_minutes": 60}}
{"scenario": "urgent", "nature": "simulation", "request": {"difficulty": 3, "high_impact": false, "can_wait": false, "deadline_minutes": 5, "budget": 0.3}, "result": {"action": "run", "resource": "senior-api", "cash": 0.3, "checks": "read-only execution and value check", "reason": "available route within the authorised budget"}}
{"scenario": "budget exhausted", "nature": "simulation", "request": {"difficulty": 3, "high_impact": false, "can_wait": false, "deadline_minutes": 120, "budget": 0}, "result": {"action": "abstain", "resource": null, "cash": 0, "checks": "read-only execution and value check", "reason": "no eligible resource within deadline and budget"}}
{"scenario": "high impact", "nature": "simulation", "request": {"difficulty": 3, "high_impact": true, "can_wait": true, "deadline_minutes": 120, "budget": 0.3}, "result": {"action": "run", "resource": "senior-subscription", "cash": 0, "checks": "source verification and human review", "reason": "eligible included capacity"}}
{"scenario": "unknown capability", "nature": "simulation", "request": {"difficulty": 4, "high_impact": false, "can_wait": true, "deadline_minutes": 120, "budget": 0.3}, "result": {"action": "abstain", "resource": null, "cash": 0, "checks": "read-only execution and value check", "reason": "no eligible resource within deadline and budget"}}
```

#### Après adaptation (modèles du portefeuille et règle du sous-groupe) 

```json
{"scenario": "simple", "nature": "simulation", "request": {"difficulty": 1, "high_impact": false, "can_wait": true, "deadline_minutes": 120, "budget": 0.3}, "result": {"action": "run", "resource": "openrouter:cohere/north-mini-code:free", "cash": 0.0, "checks": "read-only sandbox execution and non-null value check", "reason": "cheapest available zero-cash route with TD 1 capability level 1 for difficulty 1"}}
{"scenario": "complex", "nature": "simulation", "request": {"difficulty": 3, "high_impact": false, "can_wait": true, "deadline_minutes": 120, "budget": 0.3}, "result": {"action": "run", "resource": "groq:openai/gpt-oss-120b", "cash": 0.0, "checks": "SQL date/age boundary check + read-only sandbox execution", "reason": "cheapest available zero-cash route with TD 1 capability level 3 for difficulty 3"}}
{"scenario": "deferrable", "nature": "simulation", "request": {"difficulty": 3, "high_impact": false, "can_wait": true, "deadline_minutes": 120, "budget": 0.3}, "result": {"action": "defer", "resource": "groq:openai/gpt-oss-120b", "cash": 0.0, "checks": "SQL date/age boundary check + read-only sandbox execution", "reason": "free quota exhausted for groq:openai/gpt-oss-120b; deferring 60 min (within 120 min deadline) and rechecking at wake-up", "wake_in_minutes": 60}}
{"scenario": "urgent", "nature": "simulation", "request": {"difficulty": 3, "high_impact": false, "can_wait": false, "deadline_minutes": 5, "budget": 0.3}, "result": {"action": "run", "resource": "groq:openai/gpt-oss-120b:developer-paid", "cash": 0.00075, "checks": "SQL date/age boundary check + read-only sandbox execution", "reason": "free quotas unavailable or urgent; routed to paid groq:openai/gpt-oss-120b:developer-paid ($0.000750 <= budget $0.3)"}}
{"scenario": "budget exhausted", "nature": "simulation", "request": {"difficulty": 3, "high_impact": false, "can_wait": false, "deadline_minutes": 120, "budget": 0}, "result": {"action": "abstain", "resource": null, "cash": 0.0, "checks": "SQL date/age boundary check + read-only sandbox execution", "reason": "no reliable resource available for difficulty 3 within deadline (120 min) and budget ($0); refusing fallback to low-accuracy TD 1 models"}}
{"scenario": "high impact", "nature": "simulation", "request": {"difficulty": 3, "high_impact": true, "can_wait": true, "deadline_minutes": 120, "budget": 0.3}, "result": {"action": "run", "resource": "groq:openai/gpt-oss-120b", "cash": 0.0, "checks": "2-of-3 quorum (or dual OSS check on age/combinations) + reference/human review", "reason": "cheapest available zero-cash route with TD 1 capability level 3 for difficulty 3"}}
{"scenario": "unknown capability", "nature": "simulation", "request": {"difficulty": 4, "high_impact": false, "can_wait": true, "deadline_minutes": 120, "budget": 0.3}, "result": {"action": "abstain", "resource": null, "cash": 0.0, "checks": "SQL date/age boundary check + read-only sandbox execution", "reason": "no reliable resource available for difficulty 4 within deadline (120 min) and budget ($0.3); refusing fallback to low-accuracy TD 1 models"}}
```


### 2. Explication des changements faits dans `atelier-routage.py` et des raisons (pour la revue croisée & le quiz)

Voici exactement ce qui a été modifié entre la version initiale[cite: 3] et la version adaptée[cite: 4], et pourquoi :

1. **Remplacement des 3 ressources fictives (`RESOURCES`) par les modèles réels du portefeuille :**
   * *Avant:* `small-free` (niveau 1), `senior-subscription` (niveau 3), `senior-api` (niveau 3, $0.30).
   * *Après:*
     * **Niveau 1 (`period` et `product list`) :** `openrouter:cohere/north-mini-code:free` et `openrouter:dots-studio/dots-3-note-preview:free` (`cash: 0.0`, `allocation: 0.0`). Ils ont 100 % sur ces deux familles au TD 1 et sont sur route gratuite `:free`. `qwen/qwen3.8-27b` n'est pas mis en premier choix car il est beaucoup plus cher ($0.80 / $4.00 par million de tokens) pour le même score (100 %) sur ces familles simples.
     * **Niveau 2 (`age at the order` et `combinations`) :** `groq:openai/gpt-oss-20b` (`access: "subscription"`, `cash: 0.0` sur quota Groq Free, et `allocation: 0.000375` correspondant au coût implicite d'une enveloppe de 1k tokens entrée + 1k tokens sortie au tarif Developer de $0.075 + $0.30 / 1M).
     * **Niveau 3 (`completed age at a date` + requêtes complexes) :** `groq:openai/gpt-oss-120b` (`cash: 0.0` sur quota Groq Free, `allocation: 0.00075` pour 1k+1k tokens au tarif Developer de $0.15 + $0.60 / 1M), doublé d'une ressource payante `groq:openai/gpt-oss-120b:developer-paid` (`access: "tokens"`, `cash: 0.00075`) lorsque le quota gratuit est épuisé (`exhausted`).

2. **Adaptation des contrôles (`checks`) dans `choose` selon la difficulté et l'impact :**
   * *Avant:* Deux niveaux génériques (`read-only execution and value check` vs `source verification and human review`).
   * *Après :* Trois niveaux adaptés aux erreurs observées au TD 1 :
     * Pour `difficulty == 1` et `high_impact == False` : contrôle léger (`read-only sandbox execution and non-null value check`) car aucun des modèles de niveau 1 n'a échoué sur les périodes ou listes de produits.
     * Pour `difficulty >= 2` et `high_impact == False` : contrôle ciblé sur les bornes SQL (`SQL date/age boundary check + read-only sandbox execution`), car les échecs du TD 1 (y compris les faux consensus sur `C09` et `C10`) proviennent d'erreurs de bornes sur les dates et les âges.
     * Pour `high_impact == True` : contrôle renforcé (`2-of-3 quorum (or dual OSS check on age/combinations) + reference/human review`), en précisant bien de ne pas faire confiance à un quorum incluant Cohere/Qwen sur les âges.

3. **Traçabilité et lisibilité des raisons (`reason`) dans les traces :**
   * *Avant :* Raisons génériques et identiques d'un scénario à l'autre (`"eligible included capacity"`, `"no eligible resource within deadline and budget"`).
   * *Après:* Chaque décision (`run`, `defer`, `abstain`) embarque dans `reason` les paramètres concrets de la décision (niveau de capacité TD 1 requis vs obtenu, délai de réveil `wake_in_minutes` comparé à la `deadline_minutes`, coût unitaire comparé au `budget`, et refus explicite de repli vers les modèles peu fiables au TD 1 lorsque le budget ou le quota est épuisé).
   * *Point clé à retenir pour le quiz sur le scénario `deferrable` :* Quand la requête est différée (`action: "defer"`, `wake_in_minutes: 60`), le simulateur ne lance pas la requête automatiquement à l'aveugle : il indique qu'il faudra **revérifier la disponibilité au réveil** (`rechecking at wake-up`), car l'expiration d'un délai de reset ne garantit pas que le quota est effectivement revenu.