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

## Mechanism illustrated: DEMO-VOTE (constructed teaching data)

This is a one-row toy example, not a model trace and not a query on the shop database. The independent expected value is 100 cents: the sale on 2026-01-01 belongs to the requested period, whose start is inclusive and end is exclusive. The proposals are `[0, 0, 100]`, with **n=3, k=2**.

Two proposals use the faulty strict lower bound:

```sql
SELECT COALESCE(SUM(amount_cents), 0) AS revenue_cents
FROM sale
WHERE sale_date > '2026-01-01'
	AND sale_date < '2026-01-02';
```

The third uses the correct inclusive lower bound:

```sql
SELECT COALESCE(SUM(amount_cents), 0) AS revenue_cents
FROM sale
WHERE sale_date >= '2026-01-01'
	AND sale_date < '2026-01-02';
```

Both statements were executed against a temporary in-memory SQLite table containing only `('2026-01-01', 100)`. The strict `>` excludes the sale exactly at the start boundary and returns **0**; `>=` includes it and returns **100**. Thus 0 wins this constructed 2-of-3 vote despite disagreeing with the independent 100-cent reference. This toy has only three proposals, so a 3-of-5 result does not apply. The actual five-model comparison and both quorum thresholds are reported in `td2.md` for C09.

## Historical shop case: DEMO-SQL-C11

**Source and nature:** historical September 2026 pilot example supplied for this analysis; it is not claimed to be a shared-wrong case in the current 100-row `traces-td1.csv`. The question asks for all order revenue excluding VAT from customers exactly 25 years old on **2026-12-01**. The two distinct historical models, Groq `openai/gpt-oss-20b` (M1) and OpenRouter `cohere/north-mini-code:free` (M2), both execute successfully and return **0 cents** on `data/boutique.sqlite`.

The independent C11 value in [`reference-td1.csv`](../reference-td1.csv) is **446,690 cents**. Its age predicate is `birth_date > '2000-12-01' AND birth_date <= '2001-12-01'`. The supplied reference query was also executed on the database and returned 446,690.

### Historical model queries and faulty windows

M1, `openai/gpt-oss-20b`:

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date = '2001-12-01';
```

The equality tests only customers whose birthday is exactly 2001-12-01. It omits all other customers in the required interval `('2000-12-01', '2001-12-01']`; this dataset has no orders for a customer born exactly on 2001-12-01, so M1 returns 0.

M2, `cohere/north-mini-code:free`:

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE CAST(strftime('%Y-%m-%d', '2026-12-01') AS TEXT) >= c.birth_date
	AND CAST(strftime('%Y-%m-%d', '2026-12-01', '+1 year') AS TEXT) <= c.birth_date;
```

These conditions require `birth_date <= '2026-12-01'` and `birth_date >= '2027-12-01'` at the same time. The interval is contradictory and contains no birth date, so M2 returns 0. It does not express the required age-25 window.

### Executed C11 customer-level delta diagnostic

This read-only query was executed on `data/boutique.sqlite`. The CTE selects exactly the customers in the independent C11 age window, then reports their total order revenue, what each faulty predicate counts for them, and the cents each model query misses.

```sql
WITH eligible AS (
		SELECT c.customer_id, c.birth_date,
					 SUM(o.quantity_product * p.price) AS reference_cents,
					 SUM(CASE WHEN c.birth_date = '2001-12-01'
										THEN o.quantity_product * p.price ELSE 0 END) AS m1_cents,
					 SUM(CASE WHEN CAST(strftime('%Y-%m-%d', '2026-12-01') AS TEXT) >= c.birth_date
											AND CAST(strftime('%Y-%m-%d', '2026-12-01', '+1 year') AS TEXT) <= c.birth_date
										THEN o.quantity_product * p.price ELSE 0 END) AS m2_cents
		FROM customers c
		JOIN orders o ON o.customer_id = c.customer_id
		JOIN product p ON p.product_id = o.product_id
		WHERE c.birth_date > date('2026-12-01', '-26 years')
			AND c.birth_date <= date('2026-12-01', '-25 years')
		GROUP BY c.customer_id, c.birth_date
)
SELECT customer_id, birth_date, reference_cents,
			 m1_cents, reference_cents - m1_cents AS m1_missed_cents,
			 m2_cents, reference_cents - m2_cents AS m2_missed_cents
FROM eligible
ORDER BY customer_id;
```

Executed result, in euro cents:

| customer_id | birth_date | reference_cents | m1_cents | m1_missed_cents | m2_cents | m2_missed_cents |
|---|---|---:|---:|---:|---:|---:|
| C001 | 2001-09-25 | 135,000 | 0 | 135,000 | 0 | 135,000 |
| C002 | 2001-09-24 | 25,920 | 0 | 25,920 | 0 | 25,920 |
| C003 | 2001-09-26 | 47,900 | 0 | 47,900 | 0 | 47,900 |
| C006 | 2001-11-30 | 77,450 | 0 | 77,450 | 0 | 77,450 |
| C008 | 2001-05-15 | 99,090 | 0 | 99,090 | 0 | 99,090 |
| C009 | 2001-03-10 | 61,330 | 0 | 61,330 | 0 | 61,330 |
| **Total** |  | **446,690** | **0** | **446,690** | **0** | **446,690** |

As an independent check, the reference value was read from C11 in `reference-td1.csv`, then its SQL was run directly against the database. The diagnostic applies that same correct date window but aggregates by `customer_id`; the six customer amounts sum to **446,690 cents**, matching the reference. Running the two supplied historical model queries independently gives **0** for each, so the diagnostic accounts for the complete 446,690-cent difference.

The historical description provides only the two agreeing model outputs, not the other three proposals needed to evaluate a five-model 3-of-5 quorum, nor a complete fixed-panel C11 vote. Therefore no C11 3-of-5 or fixed-panel outcome is inferred from this historical example. The current-batch C09 section in `td2.md` provides the supported fixed 2-of-3 and five-model 3-of-5 results.