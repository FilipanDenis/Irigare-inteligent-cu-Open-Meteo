# CP03 - Gateway, backend și stocare SQLite

- **Proiect:** Irigare inteligentă cu Open-Meteo
- **Echipa:** Filipan Cristian Denis și Oana Rareș
- **Disciplina:** Tehnici de programare în IoT (TPI)

În CP02, gateway-ul primea date de la trei senzori virtuali. În CP03, gateway-ul trimite fiecare citire către un backend separat. Backend-ul salvează pachetul în SQLite și răspunde cu `HTTP 201` și ID-ul citirii numai după salvare.

| Traseu | Ce se întâmplă |
| --- | --- |
| Senzori → gateway | Trei procese trimit mesaje JSON prin TCP la `127.0.0.1:5050`. |
| Gateway → backend | Gateway-ul adaugă ora recepției (`primit_la`) și trimite câte un `POST /citiri` la `127.0.0.1:8303`. |
| Backend → SQLite | Backend-ul validează pachetul, salvează un rând în tabela `citiri` și întoarce ID-ul lui. |

Pentru această demonstrație, toate procesele rulează pe același calculator. Cele 24 de valori orare pentru fiecare senzor provin din `date_sintetice.csv`. Datele sunt sintetice.

## Rulare rapidă

Intră cu terminalul în folderul `CP03_irigare`. Ai nevoie de Python 3, fără pachete instalate prin `pip`.

```
python3 demo.py
```

Scriptul pornește backend-ul, gateway-ul și cei trei senzori. Trimite accelerat cele **72 de citiri** și afișează exemple de confirmări `HTTP 201` și rânduri salvate. Apoi oprește procesele și citește baza direct de pe disc, cu `verifica.py`.

La final trebuie să vezi câte `24/24` citiri pentru `temperatura`, `ploaie` și `et0`, apoi `OK: 72/72 citiri din baza corespund sursei.` Baza și jurnalele rămân în directorul indicat de program, sub `rulari/`. Fiecare demonstrație folosește o bază nouă.

## Rulare manuală

Deschide terminalele în folderul `CP03_irigare` și pornește în ordinea aceasta:

| Terminal | Comandă |
| --- | --- |
| 1 | `python3 backend.py` |
| 2 | `python3 gateway.py` |
| 3 | `python3 senzor.py temperatura` |
| 4 | `python3 senzor.py ploaie` |
| 5 | `python3 senzor.py et0` |

Așteaptă ca backend-ul și gateway-ul să afișeze adresele pe care ascultă înainte de a porni senzorii. După ce termină cei trei senzori și gateway-ul afișează deconectarea fiecăruia, oprește gateway-ul și backend-ul cu `Ctrl+C`. Rulează apoi:

```
python3 verifica.py
```

Verificarea citește `irigare.db` direct și compară valorile, numerele mesajelor, unitățile și timestamp-urile cu CSV-ul. Backend-ul păstrează datele la repornire, deci pentru un nou test manual poți porni `python3 backend.py --db proba2.db` și verifica cu `python3 verifica.py --db proba2.db`.

Dacă apare `Address already in use`, verifică dacă ai lăsat pornit un gateway pe portul `5050` sau un backend pe `8303`.

## Ce se vede în capturi

- La gateway, `HTTP 201 | id=...` confirmă pachetul trimis și salvat. La backend, linia cu același ID arată citirea introdusă în SQLite.
- Verificarea grupează rândurile din baza de date după senzor. Fiecare din cele trei surse are 24 de citiri, inclusiv după oprirea backend-ului.

`timestamp` este ora simulată a citirii, iar `primit_la` este ora la care gateway-ul a primit-o. Dacă backend-ul nu răspunde sau respinge pachetul, gateway-ul afișează `Fara confirmare`. În demonstrație nu se retrimit automat pachetele.

Raportul cu capturi și explicații este în [Raport_CP03.pdf](Raport_CP03.pdf).
