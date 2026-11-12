import argparse
from collections import Counter
from contextlib import closing
import csv
from datetime import datetime
from pathlib import Path
import sqlite3


UNITATI = {"temperatura": "C", "ploaie": "mm", "et0": "mm"}


def verifica(cale_baza):
    sursa_csv = Path(__file__).with_name("date_sintetice.csv")
    with sursa_csv.open(newline="", encoding="utf-8") as fisier:
        sursa = list(csv.DictReader(fisier))
    uri_baza = Path(cale_baza).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri_baza, uri=True)) as db:
        randuri = db.execute("SELECT senzor, nr, timestamp, valoare, unitate, sursa, primit_la "
                             "FROM citiri ORDER BY id").fetchall()
        grupuri = dict(db.execute("SELECT senzor, COUNT(*) FROM citiri GROUP BY senzor"))
    print(f"Baza SQLite: {cale_baza}")
    print("SELECT senzor, COUNT(*) FROM citiri GROUP BY senzor;")
    for senzor in UNITATI:
        print(f"  {senzor:11s}: {grupuri.get(senzor, 0)}/{len(sursa)} citiri")

    asteptate = Counter(
        (senzor, nr, rand["timestamp"], float(rand[senzor]), unitate, "sintetic")
        for nr, rand in enumerate(sursa, 1)
        for senzor, unitate in UNITATI.items()
    )
    gasite = Counter(rand[:-1] for rand in randuri)
    for rand in randuri:
        datetime.fromisoformat(rand[-1])
    if gasite != asteptate:
        lipsa = sum((asteptate - gasite).values())
        extra = sum((gasite - asteptate).values())
        raise ValueError(f"{lipsa} citiri lipsa sau diferite, {extra} citiri in plus")
    print(f"OK: {len(randuri)}/{sum(asteptate.values())} citiri din baza corespund sursei.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compara citirile din SQLite cu fisierul de test.")
    parser.add_argument("--db", default="irigare.db", help="fisierul SQLite")
    args = parser.parse_args()
    try:
        verifica(args.db)
    except (OSError, ValueError, TypeError, KeyError, sqlite3.Error) as eroare:
        raise SystemExit(f"EROARE: {eroare}")
