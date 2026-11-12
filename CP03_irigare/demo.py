import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


SENZORI = ("temperatura", "ploaie", "et0")


def asteapta(proces, jurnal, text, aparitii=1):
    limita = time.monotonic() + 10
    while time.monotonic() < limita:
        continut = jurnal.read_text(encoding="utf-8", errors="replace")
        if continut.count(text) >= aparitii:
            return continut
        if proces.poll() is not None:
            break
        time.sleep(0.05)
    raise RuntimeError(f"Nu am gasit '{text}' in {jurnal}.\n{continut}")


def demo():
    os.chdir(Path(__file__).resolve().parent)
    Path("rulari").mkdir(exist_ok=True)
    dosar = Path(tempfile.mkdtemp(prefix="test-", dir="rulari")).resolve().relative_to(Path.cwd())
    baza = dosar / "irigare.db"
    procese = []

    def porneste(nume, *argumente):
        jurnal = dosar / f"{nume}.log"
        with jurnal.open("w", encoding="utf-8") as iesire:
            proces = subprocess.Popen([sys.executable, "-u", *argumente],
                                      stdout=iesire, stderr=subprocess.STDOUT)
        procese.append(proces)
        return proces, jurnal

    print("CP03 | Senzori -> Gateway -> Backend -> SQLite", flush=True)
    try:
        backend, log_backend = porneste("backend", "backend.py", "--db", str(baza))
        print(asteapta(backend, log_backend, "Baza SQLite:").strip(), flush=True)
        gateway, log_gateway = porneste("gateway", "gateway.py")
        print(asteapta(gateway, log_gateway, "Astept senzori.").strip(), flush=True)

        clienti = [porneste(senzor, "senzor.py", senzor, "--interval", "0.1") for senzor in SENZORI]
        print("Senzori: " + ", ".join(f"{senzor} PID={client.pid}"
                                     for senzor, (client, _) in zip(SENZORI, clienti)), flush=True)
        for client, jurnal in clienti:
            if client.wait(timeout=20) != 0:
                raise RuntimeError(jurnal.read_text(encoding="utf-8", errors="replace"))

        gateway_log = asteapta(gateway, log_gateway, "Senzor deconectat:", len(SENZORI))
        confirmari = [linie for linie in gateway_log.splitlines() if "HTTP 201 | id=" in linie]
        stocari = [linie for linie in log_backend.read_text(encoding="utf-8").splitlines()
                   if "Stocat in SQLite | id=" in linie]
        if not confirmari or len(confirmari) != len(stocari) or "Fara confirmare:" in gateway_log:
            raise RuntimeError(f"Transmisie incompleta. Vezi jurnalele din {dosar}.")

        print(f"\nGateway: {len(confirmari)} confirmari HTTP 201. Exemple:")
        for senzor in SENZORI:
            print(next(linie for linie in reversed(confirmari) if f"| {senzor} nr=" in linie))
        print(f"\nBackend: {len(stocari)} citiri stocate. Exemple:")
        for senzor in SENZORI:
            print(next(linie for linie in reversed(stocari) if f"| {senzor} nr=" in linie))
    finally:
        for proces in reversed(procese):
            if proces.poll() is None:
                proces.terminate()
                try:
                    proces.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proces.kill()
                    proces.wait()

    print("\nGateway si backend oprite. Citesc baza de pe disc.", flush=True)
    print(f"Verificare: python3 verifica.py --db {baza}", flush=True)
    subprocess.run([sys.executable, "verifica.py", "--db", str(baza)], check=True)


if __name__ == "__main__":
    try:
        demo()
    except (OSError, RuntimeError, subprocess.SubprocessError) as eroare:
        raise SystemExit(f"EROARE: {eroare}")
