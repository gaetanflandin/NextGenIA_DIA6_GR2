-- TD1 reference queries. Open data/boutique.sqlite and run these SELECT statements.
-- Revenue is in euro cents excluding VAT. Each query returns one revenue_cents value.

-- C01 | expected revenue_cents: 792800
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE o.date >= '2026-03-01 00:00:00' AND o.date < '2026-06-01 00:00:00';

-- C02 | expected revenue_cents: 590320
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE (CAST(strftime('%Y', '2026-09-25') AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) - (strftime('%m-%d', '2026-09-25') < strftime('%m-%d', c.birth_date))) = 25;

-- C03 | expected revenue_cents: 936350
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE o.date >= '2026-01-01 00:00:00' AND o.date < '2026-07-01 00:00:00' AND o.product_id IN ('a', 'b', 'c');

-- C04 | expected revenue_cents: 2826250
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE o.date >= '2026-01-01 00:00:00' AND o.date < '2026-10-01 00:00:00';

-- C05 | expected revenue_cents: 38480
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE o.date >= '2026-06-01 00:00:00' AND o.date < '2026-06-02 00:00:00';

-- C06 | expected revenue_cents: 0
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE o.date >= '2025-01-01 00:00:00' AND o.date < '2026-01-01 00:00:00';

-- C07 | expected revenue_cents: 13970
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE o.date >= '2026-05-31 00:00:00' AND o.date < '2026-06-01 00:00:00';

-- C08 | expected revenue_cents: 605580
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE (CAST(strftime('%Y', '2026-09-24') AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) - (strftime('%m-%d', '2026-09-24') < strftime('%m-%d', c.birth_date))) = 25;

-- C09 | expected revenue_cents: 487980
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE (CAST(strftime('%Y', '2026-09-26') AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) - (strftime('%m-%d', '2026-09-26') < strftime('%m-%d', c.birth_date))) = 25;

-- C10 | expected revenue_cents: 558980
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE (CAST(strftime('%Y', o.date) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) - (strftime('%m-%d', o.date) < strftime('%m-%d', c.birth_date))) = 25;

-- C11 | expected revenue_cents: 446690
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE (CAST(strftime('%Y', '2026-12-01') AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) - (strftime('%m-%d', '2026-12-01') < strftime('%m-%d', c.birth_date))) = 25;

-- C12 | expected revenue_cents: 1666490
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE o.product_id IN ('a', 'b', 'c');

-- C13 | expected revenue_cents: 107740
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE o.date >= '2026-04-01 00:00:00' AND o.date < '2026-05-01 00:00:00' AND o.product_id IN ('a', 'c');

-- C14 | expected revenue_cents: 0
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE o.date >= '2026-10-01 00:00:00' AND o.date < '2026-12-01 00:00:00' AND o.product_id IN ('a', 'b', 'c');

-- C15 | expected revenue_cents: 168680
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE o.date >= '2026-03-01 00:00:00' AND o.date < '2026-06-01 00:00:00' AND (CAST(strftime('%Y', '2026-09-25') AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) - (strftime('%m-%d', '2026-09-25') < strftime('%m-%d', c.birth_date))) = 25;

-- C16 | expected revenue_cents: 376740
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE (CAST(strftime('%Y', '2026-09-25') AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) - (strftime('%m-%d', '2026-09-25') < strftime('%m-%d', c.birth_date))) = 25 AND o.product_id IN ('a', 'b', 'c');

-- C17 | expected revenue_cents: 258180
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE o.date >= '2026-01-01 00:00:00' AND o.date < '2026-07-01 00:00:00' AND (CAST(strftime('%Y', '2026-09-25') AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) - (strftime('%m-%d', '2026-09-25') < strftime('%m-%d', c.birth_date))) = 25 AND o.product_id IN ('a', 'b', 'c');

-- C18 | expected revenue_cents: 62480
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE o.date >= '2026-05-01 00:00:00' AND o.date < '2026-06-01 00:00:00' AND (CAST(strftime('%Y', o.date) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) - (strftime('%m-%d', o.date) < strftime('%m-%d', c.birth_date))) = 25;

-- C19 | expected revenue_cents: 1990
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE o.date >= '2026-09-01 00:00:00' AND o.date < '2026-10-01 00:00:00' AND (CAST(strftime('%Y', '2026-09-25') AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) - (strftime('%m-%d', '2026-09-25') < strftime('%m-%d', c.birth_date))) = 25 AND o.product_id IN ('d');

-- C20 | expected revenue_cents: 1106090
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p USING (product_id) JOIN customers AS c USING (customer_id) WHERE o.date >= '2026-06-01 00:00:00' AND o.date < '2026-09-01 00:00:00';
