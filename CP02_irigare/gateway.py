import csv
import json
import math
import os
import socket
import threading
from datetime import datetime


IP = "127.0.0.1"
PORT = 5050
UNITATI = {"temperatura": "C", "ploaie": "mm", "et0": "mm"}
COLOANE = ["primit_la", "senzor", "nr", "timestamp", "valoare", "unitate", "sursa"]
blocare = threading.Lock()
total = 0


def primeste(conexiune, adresa):
    global total
    nume = threading.current_thread().name
    with blocare:
        print(f"[{nume}] Conectat: {adresa}", flush=True)
    try:
        with conexiune, conexiune.makefile("r", encoding="utf-8") as flux:
            for linie in flux:
                try:
                    mesaj = json.loads(linie)
                    senzor = mesaj["senzor"]
                    nr = mesaj["nr"]
                    moment = mesaj["timestamp"]
                    valoare = float(mesaj["valoare"])
                    if senzor not in UNITATI or mesaj["unitate"] != UNITATI[senzor]:
                        raise ValueError("senzor sau unitate necunoscuta")
                    if type(nr) is not int or nr < 1 or not math.isfinite(valoare):
                        raise ValueError("numar sau valoare incorecta")
                    datetime.fromisoformat(moment)
                    if mesaj["sursa"] != "sintetic":
                        raise ValueError("sursa neasteptata")
                    rand = [datetime.now().astimezone().isoformat(timespec="seconds"),
                            senzor, nr, moment, valoare, mesaj["unitate"], mesaj["sursa"]]
                except (ValueError, KeyError, TypeError) as eroare:
                    with blocare:
                        print(f"[{nume}] Mesaj ignorat: {eroare}", flush=True)
                    continue
                with blocare:
                    with open("date_primite.csv", "a", newline="", encoding="utf-8") as fisier:
                        csv.writer(fisier).writerow(rand)
                    total += 1
                    print(f"[{nume}] #{total:03d} {senzor:11s} nr={nr:02d} "
                          f"ora={moment[11:16]} valoare={valoare:.2f} {mesaj['unitate']}",
                          flush=True)
    except (OSError, UnicodeError) as eroare:
        with blocare:
            print(f"[{nume}] Conexiune intrerupta: {eroare}", flush=True)
    finally:
        with blocare:
            print(f"[{nume}] Deconectat: {adresa}", flush=True)


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((IP, PORT))
        server.listen()
        with open("date_primite.csv", "w", newline="", encoding="utf-8") as fisier:
            csv.writer(fisier).writerow(COLOANE)
        print(f"Gateway PID={os.getpid()} | TCP {IP}:{PORT}", flush=True)
        print("Astept senzori. Datele se salveaza in date_primite.csv.", flush=True)
        try:
            while True:
                conexiune, adresa = server.accept()
                threading.Thread(target=primeste, args=(conexiune, adresa), daemon=True).start()
                with blocare:
                    print(f"[Gateway] Thread-uri active: {threading.active_count()}", flush=True)
        except KeyboardInterrupt:
            print(f"\nGateway oprit. Total primit: {total}", flush=True)
