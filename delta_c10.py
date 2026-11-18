import sqlite3

con = sqlite3.connect("data/boutique.sqlite")

requete = """
WITH base AS (
  SELECT o.customer_id,
         o.quantity_product * p.price AS rev,
         CAST(strftime('%Y',o.date) AS INTEGER)
           - CAST(strftime('%Y',c.birth_date) AS INTEGER)
           - (strftime('%m-%d',o.date) < strftime('%m-%d',c.birth_date)) AS age_ref,
         CAST(strftime('%Y',o.date) AS INTEGER)
           - CAST(strftime('%Y',c.birth_date) AS INTEGER) AS diff_annees
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN product  p USING (product_id)
)
SELECT customer_id, COUNT(*) AS lignes, SUM(rev) AS revenu_manque_cents
FROM base
WHERE age_ref = 25 AND diff_annees = 26
GROUP BY customer_id
ORDER BY customer_id;
"""

total = 0
for ligne in con.execute(requete):
    print(ligne)
    total += ligne[2]

print("Total manque :", total)
print("Ecart attendu :", 558980 - 119410)