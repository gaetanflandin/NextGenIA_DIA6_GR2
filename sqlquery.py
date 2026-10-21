import csv
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATABASE = HERE / "data" / "boutique.sqlite"
REFERENCE = HERE / "reference-td1.csv"

PERIODS = {
    "C01": ("2026-03-01 00:00:00", "2026-06-01 00:00:00"),
    "C03": ("2026-01-01 00:00:00", "2026-07-01 00:00:00"),
    "C04": ("2026-01-01 00:00:00", "2026-10-01 00:00:00"),
    "C05": ("2026-06-01 00:00:00", "2026-06-02 00:00:00"),
    "C06": ("2025-01-01 00:00:00", "2026-01-01 00:00:00"),
    "C07": ("2026-05-31 00:00:00", "2026-06-01 00:00:00"),
    "C13": ("2026-04-01 00:00:00", "2026-05-01 00:00:00"),
    "C14": ("2026-10-01 00:00:00", "2026-12-01 00:00:00"),
    "C15": ("2026-03-01 00:00:00", "2026-06-01 00:00:00"),
    "C17": ("2026-01-01 00:00:00", "2026-07-01 00:00:00"),
    "C18": ("2026-05-01 00:00:00", "2026-06-01 00:00:00"),
    "C19": ("2026-09-01 00:00:00", "2026-10-01 00:00:00"),
    "C20": ("2026-06-01 00:00:00", "2026-09-01 00:00:00"),
}
REFERENCE_DATES = {
    "C02": "2026-09-25",
    "C08": "2026-09-24",
    "C09": "2026-09-26",
    "C11": "2026-12-01",
    "C15": "2026-09-25",
    "C16": "2026-09-25",
    "C17": "2026-09-25",
    "C19": "2026-09-25",
}
PRODUCTS = {
    "C03": ("a", "b", "c"),
    "C12": ("a", "b", "c"),
    "C13": ("a", "c"),
    "C14": ("a", "b", "c"),
    "C16": ("a", "b", "c"),
    "C17": ("a", "b", "c"),
    "C19": ("d",),
}
AGE_AT_ORDER = {"C10", "C18"}


def build_query(case_id: str) -> str:
    filters = []
    if case_id in PERIODS:
        start, end = PERIODS[case_id]
        filters.extend((f"o.date >= '{start}'", f"o.date < '{end}'"))
    if case_id in REFERENCE_DATES:
        reference_date = REFERENCE_DATES[case_id]
        filters.append(
            f"c.birth_date > date('{reference_date}', '-26 years') "
            f"AND c.birth_date <= date('{reference_date}', '-25 years')"
        )
    elif case_id in AGE_AT_ORDER:
        filters.append(
            "c.birth_date > date(o.date, '-26 years') "
            "AND c.birth_date <= date(o.date, '-25 years')"
        )
    if case_id in PRODUCTS:
        products = ", ".join(f"'{product}'" for product in PRODUCTS[case_id])
        filters.append(f"p.product_id IN ({products})")

    query = (
        "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents "
        "FROM orders AS o "
        "JOIN product AS p ON p.product_id = o.product_id "
        "JOIN customers AS c ON c.customer_id = o.customer_id"
    )
    if filters:
        query += " WHERE " + " AND ".join(f"({item})" for item in filters)
    return query


def main() -> None:
    if not DATABASE.exists():
        raise FileNotFoundError(f"Database not found: {DATABASE}")
    if not (HERE / "questions-td1-en.md").exists():
        raise FileNotFoundError(f"Questions file not found: {HERE / 'questions-td1-en.md'}")

    with sqlite3.connect(f"{DATABASE.as_uri()}?mode=ro", uri=True) as connection:
        results = []
        for index in range(1, 21):
            case_id = f"C{index:02d}"
            query = build_query(case_id)
            cursor = connection.execute(query)
            columns = [column[0] for column in cursor.description or ()]
            row = cursor.fetchone()
            if columns != ["revenue_cents"] or row is None or cursor.fetchone() is not None:
                raise ValueError(f"{case_id}: query must return exactly one row named revenue_cents")
            results.append((case_id, query, row[0]))

    with REFERENCE.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("case_id", "sql", "revenue_cents"))
        writer.writerows(results)

    for case_id, _, revenue in results:
        print(f"{case_id}: {revenue}")


if __name__ == "__main__":
    main()