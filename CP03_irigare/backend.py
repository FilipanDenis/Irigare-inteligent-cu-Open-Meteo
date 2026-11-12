import argparse
from contextlib import closing
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import math
import os
import sqlite3


IP = "127.0.0.1"
PORT = 8303
UNITATI = {"temperatura": "C", "ploaie": "mm", "et0": "mm"}


def citire_din_pachet(pachet):
    senzor = pachet["senzor"]
    nr = pachet["nr"]
    moment = pachet["timestamp"]
    valoare = pachet["valoare"]
    unitate = pachet["unitate"]
    sursa = pachet["sursa"]
    primit_la = pachet["primit_la"]
    if senzor not in UNITATI or unitate != UNITATI[senzor] or sursa != "sintetic":
        raise ValueError("senzor, unitate sau sursa incorecta")
    if type(nr) is not int or not 1 <= nr <= 2**63 - 1:
        raise ValueError("numar de mesaj incorect")
    if type(valoare) not in (int, float) or not math.isfinite(valoare):
        raise ValueError("valoare incorecta")
    datetime.fromisoformat(moment)
    datetime.fromisoformat(primit_la)
    return senzor, nr, moment, valoare, unitate, sursa, primit_la


class Receptor(BaseHTTPRequestHandler):
    timeout = 5

    def log_message(self, format, *args):
        pass

    def raspunde(self, cod, continut):
        corp = json.dumps(continut).encode("utf-8")
        self.send_response(cod)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(corp)))
        self.end_headers()
        self.wfile.write(corp)

    def do_POST(self):
        if self.path != "/citiri":
            self.raspunde(404, {"eroare": "ruta este /citiri"})
            return
        try:
            lungime = int(self.headers.get("Content-Length", "0"))
            if not 1 <= lungime <= 4096:
                raise ValueError("lungime incorecta")
            pachet = json.loads(self.rfile.read(lungime))
            rand = citire_din_pachet(pachet)
        except (ValueError, TypeError, KeyError, OverflowError):
            self.raspunde(400, {"eroare": "pachet invalid"})
            return

        db = self.server.db
        try:
            with db:
                rezultat = db.execute(
                    "INSERT INTO citiri (senzor, nr, timestamp, valoare, unitate, sursa, primit_la) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)", rand
                )
                id_citire = rezultat.lastrowid
        except sqlite3.Error as eroare:
            print(f"[Backend] Eroare SQLite: {eroare}", flush=True)
            self.raspunde(500, {"eroare": "salvarea a esuat"})
            return

        print(f"[Backend] Stocat in SQLite | id={id_citire} | {rand[0]} nr={rand[1]:02d}", flush=True)
        self.raspunde(201, {"id": id_citire})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Primeste pachete JSON si le salveaza in SQLite.")
    parser.add_argument("--db", default="irigare.db", help="fisierul SQLite")
    args = parser.parse_args()

    with HTTPServer((IP, PORT), Receptor) as server, closing(sqlite3.connect(args.db, timeout=2)) as db:
        server.db = db
        with db:
            db.execute("""CREATE TABLE IF NOT EXISTS citiri (
                id INTEGER PRIMARY KEY,
                senzor TEXT NOT NULL, nr INTEGER NOT NULL,
                timestamp TEXT NOT NULL, valoare REAL NOT NULL,
                unitate TEXT NOT NULL, sursa TEXT NOT NULL, primit_la TEXT NOT NULL
            )""")
        print(f"[Backend] PID={os.getpid()} | HTTP {IP}:{PORT}/citiri", flush=True)
        print(f"[Backend] Baza SQLite: {args.db}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nBackend oprit.", flush=True)
