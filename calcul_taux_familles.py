import csv
from pathlib import Path

FAMILIES = {
    "C01": "period",
    "C02": "completed age at a date",
    "C03": "product list",
    "C04": "period",
    "C05": "period",
    "C06": "period",
    "C07": "period",
    "C08": "completed age at a date",
    "C09": "completed age at a date",
    "C10": "age at the order",
    "C11": "completed age at a date",
    "C12": "product list",
    "C13": "product list",
    "C14": "product list",
    "C15": "combinations",
    "C16": "combinations",
    "C17": "combinations",
    "C18": "combinations",
    "C19": "combinations",
    "C20": "period",
}

FAMILY_ORDER = [
    "period",
    "completed age at a date",
    "age at the order",
    "product list",
    "combinations",
]

comp_path = Path("model-question-comparison-en.csv")
records = []

with comp_path.open(encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        nature = row.get("nature", "real").strip().lower()
        if nature and nature != "real":
            continue
        records.append((
            row["model_id"].strip(),
            row["case_id"].strip(),
            row["status"].strip().lower(),
        ))

models = sorted({r[0] for r in records})
stats = {(m, fam): [0, 0, []] for m in models for fam in FAMILY_ORDER}

for model, case, status in records:
    fam = FAMILIES.get(case)
    if fam:
        stats[(model, fam)][1] += 1
        if status == "correct":
            stats[(model, fam)][0] += 1
            stats[(model, fam)][2].append(case)

# Export CSV propre (taux + cellules réussies par famille)
csv_path = Path("taux-familles-td2.csv")
fieldnames = [
    "model_id",
    "period_rate", "period_cells",
    "completed_age_at_date_rate", "completed_age_at_date_cells",
    "age_at_order_rate", "age_at_order_cells",
    "product_list_rate", "product_list_cells",
    "combinations_rate", "combinations_cells",
    "global_rate",
]

with csv_path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for m in models:
        tot_ok, tot_n = 0, 0
        out_row = {"model_id": m}
        col_prefixes = [
            "period",
            "completed_age_at_date",
            "age_at_order",
            "product_list",
            "combinations",
        ]
        for fam, prefix in zip(FAMILY_ORDER, col_prefixes):
            ok, n, cases_ok = stats[(m, fam)]
            tot_ok += ok
            tot_n += n
            pct = f"{(100 * ok / n):.0f}%" if n else "N/A"
            out_row[f"{prefix}_rate"] = f"{ok}/{n} ({pct})"
            out_row[f"{prefix}_cells"] = ",".join(sorted(cases_ok)) if cases_ok else ""
        glob_pct = f"{(100 * tot_ok / tot_n):.0f}%" if tot_n else "N/A"
        out_row["global_rate"] = f"{tot_ok}/{tot_n} ({glob_pct})"
        writer.writerow(out_row)

print(f"CSV généré : {csv_path}")