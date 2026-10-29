import csv
from collections import Counter
from datetime import datetime


unitati = {"temperatura": "C", "ploaie": "mm", "et0": "mm"}
try:
    with open("date_sintetice.csv", newline="", encoding="utf-8") as fisier:
        sursa = list(csv.DictReader(fisier))
    with open("date_primite.csv", newline="", encoding="utf-8") as fisier:
        primite = list(csv.DictReader(fisier))
    asteptate = Counter(
        (senzor, nr, rand["timestamp"], float(rand[senzor]), unitate, "sintetic")
        for nr, rand in enumerate(sursa, start=1)
        for senzor, unitate in unitati.items()
    )
    gasite = Counter()
    for rand in primite:
        datetime.fromisoformat(rand["primit_la"])
        gasite[(rand["senzor"], int(rand["nr"]), rand["timestamp"],
                float(rand["valoare"]), rand["unitate"], rand["sursa"])] += 1
except (OSError, ValueError, KeyError) as eroare:
    raise SystemExit(f"EROARE: {eroare}. Ruleaza mai intai gateway-ul si cei trei senzori.")

for senzor in unitati:
    numere = [int(rand["nr"]) for rand in primite if rand["senzor"] == senzor]
    print(f"{senzor}: {len(numere)}/{len(sursa)} mesaje primite")
    if numere != list(range(1, len(sursa) + 1)):
        raise SystemExit(f"EROARE: mesaje lipsa, duplicate sau in alta ordine pentru {senzor}.")
if gasite != asteptate:
    lipsa = sum((asteptate - gasite).values())
    extra = sum((gasite - asteptate).values())
    raise SystemExit(f"EROARE: {lipsa} mesaje lipsa sau diferite; {extra} mesaje in plus.")
print(f"OK: {len(primite)} mesaje. Valorile, ordinea pe senzor, unitatile si timestamp-urile corespund sursei.")
