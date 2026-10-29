import argparse
import csv
import json
import os
import socket
import time


IP = "127.0.0.1"
PORT = 5050
UNITATI = {"temperatura": "C", "ploaie": "mm", "et0": "mm"}

parser = argparse.ArgumentParser(description="Trimite un canal de date sintetice catre gateway.")
parser.add_argument("senzor", choices=UNITATI)
parser.add_argument("--interval", type=float, default=3,
                    help="pauza reala intre mesaje, in secunde (implicit: 3)")
args = parser.parse_args()
if not 0 < args.interval <= 60:
    parser.error("intervalul trebuie sa fie intre 0 si 60 de secunde")

with open("date_sintetice.csv", newline="", encoding="utf-8") as fisier:
    date = list(csv.DictReader(fisier))

print(f"Senzor {args.senzor} | PID={os.getpid()} | sursa=sintetic", flush=True)
try:
    with socket.create_connection((IP, PORT), timeout=5) as conexiune:
        for nr, rand in enumerate(date, start=1):
            mesaj = {"senzor": args.senzor, "nr": nr, "timestamp": rand["timestamp"],
                     "valoare": float(rand[args.senzor]), "unitate": UNITATI[args.senzor],
                     "sursa": "sintetic"}
            conexiune.sendall((json.dumps(mesaj) + "\n").encode("utf-8"))
            print(f"Trimis nr={nr:02d} ora={rand['timestamp'][11:16]} "
                  f"valoare={mesaj['valoare']:.2f} {mesaj['unitate']}", flush=True)
            if nr < len(date):
                time.sleep(args.interval)
    print(f"Terminat. {len(date)} mesaje trimise.", flush=True)
except OSError as eroare:
    raise SystemExit(f"Eroare de conexiune: {eroare}. Verifica daca gateway.py este pornit.")
