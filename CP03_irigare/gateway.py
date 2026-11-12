from datetime import datetime
from http.client import HTTPConnection, HTTPException
import json
import os
import socket
import threading


IP = "127.0.0.1"
PORT_SENZORI = 5050
PORT_BACKEND = 8303
blocare = threading.Lock()


def afiseaza(text):
    with blocare:
        print(text, flush=True)


def trimite_backend(pachet):
    corp = json.dumps(pachet).encode("utf-8")
    http = HTTPConnection(IP, PORT_BACKEND, timeout=5)
    try:
        http.request("POST", "/citiri", corp, {"Content-Type": "application/json"})
        raspuns = http.getresponse()
        if raspuns.status != 201:
            raise ValueError(f"backend-ul a raspuns HTTP {raspuns.status}")
        id_citire = json.loads(raspuns.read())["id"]
        if type(id_citire) is not int or id_citire < 1:
            raise ValueError("confirmare fara ID valid")
        return id_citire
    finally:
        http.close()


def primeste(conexiune, adresa):
    afiseaza(f"[Gateway] Senzor conectat: {adresa}")
    try:
        with conexiune, conexiune.makefile("r", encoding="utf-8") as flux:
            for linie in flux:
                try:
                    pachet = json.loads(linie)
                    if not isinstance(pachet, dict):
                        raise ValueError("mesajul trebuie sa fie un obiect JSON")
                    pachet["primit_la"] = datetime.now().astimezone().isoformat(timespec="seconds")
                    id_citire = trimite_backend(pachet)
                    afiseaza(f"[Gateway] POST /citiri -> HTTP 201 | id={id_citire} | "
                             f"{pachet['senzor']} nr={pachet['nr']:02d}")
                except (ValueError, TypeError, KeyError, OSError, HTTPException) as eroare:
                    afiseaza(f"[Gateway] Fara confirmare: {eroare}")
    except (OSError, UnicodeError) as eroare:
        afiseaza(f"[Gateway] Conexiune intrerupta: {eroare}")
    finally:
        afiseaza(f"[Gateway] Senzor deconectat: {adresa}")


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((IP, PORT_SENZORI))
        server.listen()
        print(f"[Gateway] PID={os.getpid()} | TCP {IP}:{PORT_SENZORI}", flush=True)
        print(f"[Gateway] Astept senzori. Trimit la http://{IP}:{PORT_BACKEND}/citiri", flush=True)
        try:
            while True:
                conexiune, adresa = server.accept()
                threading.Thread(target=primeste, args=(conexiune, adresa), daemon=True).start()
        except KeyboardInterrupt:
            print("\nGateway oprit.", flush=True)
