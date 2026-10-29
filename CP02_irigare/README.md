# CP02 - Senzori virtuali și gateway

Etapă din proiectul **Irigare inteligentă cu Open-Meteo**, la TPI.

Trei procese Python citesc date sintetice și le trimit prin TCP către un gateway.
Gateway-ul folosește câte un thread pentru fiecare conexiune și salvează mesajele în CSV.
Totul rulează pe același laptop, cu Python 3 și biblioteca standard.

## Fișiere

| Fișier | Rol |
| --- | --- |
| `gateway.py` | Primește simultan conexiunile și scrie `date_primite.csv`. |
| `senzor.py` | Trimite un singur canal; se pornește separat de trei ori. |
| `date_sintetice.csv` | 24 de ore de date de test, generate pentru demonstrație. |
| `verifica.py` | Compară mesajele primite cu fișierul-sursă. |

## Pornire pe Fedora

Dezarhivează pachetul și intră în folderul în care sunt programele.
Deschide **mai întâi patru terminale** în același folder (clic dreapta în folder -> deschide în terminal).
Nu trebuie instalate pachete prin `pip`. Verifică Python cu `python3 --version`.

Terminalul 1 - gateway:

```
python3 gateway.py
```

Așteaptă mesajul `Astept senzori`. Apoi pornește cele trei comenzi, în terminale diferite:

Terminalul 2:

```
python3 senzor.py temperatura
```

Terminalul 3:

```
python3 senzor.py ploaie
```

Terminalul 4:

```
python3 senzor.py et0
```

Fiecare senzor trimite 24 de mesaje, unul la 3 secunde, apoi se închide.
O oră din fișier este redată la fiecare 3 secunde reale; aceasta este o accelerare a redării.
Pornește senzorii unul după altul, astfel încât să ruleze împreună.
Gateway-ul afișează nume diferite de thread și poate ajunge la 4 thread-uri active:
thread-ul principal și cele trei care primesc date.

## Verificare și oprire

După ce toți senzorii afișează `Terminat. 24 mesaje trimise.`, rulează într-un terminal liber:

```
python3 verifica.py
```

Rezultatul așteptat este 24 de mesaje pentru fiecare senzor, 72 în total, și mesajul `OK`.
Verificatorul controlează valorile, unitățile, timestamp-urile, numerele mesajelor și ordinea
lor pe fiecare senzor. Nu impune o ordine între senzori diferiți: mesajele lor pot sosi intercalat.
La final oprește gateway-ul cu `Ctrl+C`, după terminarea senzorilor.

La fiecare pornire, gateway-ul regenerează `date_primite.csv`. Pentru a păstra o rulare,
copiază acest fișier înainte să repornești gateway-ul.

## Ce reprezintă datele

- `temperatura`: temperatura aerului, în grade Celsius (`C` în mesaje).
- `ploaie`: cantitatea de ploaie din ora simulată, în mm.
- `et0`: evapotranspirația de referință din ora simulată, în mm.

**Toate valorile sunt sintetice**, inclusiv ET0. Nu sunt descărcate din Open-Meteo și nu sunt
măsurători fizice. Data de 15 iulie 2026 este o etichetă pentru scenariul de test.
Procesul ET0 emulează o sursă de date calculate, nu un senzor fizic de evaporare.
Într-o etapă ulterioară, acest CSV poate fi înlocuit cu date istorice Open-Meteo.

`timestamp` este ora simulată din CSV. `primit_la` este ora reală a recepției, adăugată de gateway.
Cele trei procese redau independent același fișier; timestamp-ul permite asocierea ulterioară
a valorilor pentru aceeași oră. În această etapă gateway-ul colectează și înregistrează datele.

## Comunicarea

Adresa este `127.0.0.1`, portul `5050`. Acesta este un exemplu cu procese separate pe același laptop.
Un mesaj JSON este terminat cu `\n`, astfel încât gateway-ul să poată separa mesajele din fluxul TCP:

```json
{"senzor":"temperatura","nr":1,"timestamp":"2026-07-15T00:00:00+03:00","valoare":18.0,"unitate":"C","sursa":"sintetic"}
```

`makefile()` permite citirea mesajelor linie cu linie, inclusiv când TCP le fragmentează sau le grupează.
`threading.Thread` tratează fiecare conexiune separat. `threading.Lock` protejează scrierea comună
în CSV și contorul mesajelor. Un client lent nu trebuie să blocheze ceilalți clienți.

Dacă apare o eroare de conectare, verifică dacă gateway-ul este pornit în primul terminal.
Dacă portul este ocupat de o rulare anterioară, oprește vechiul gateway înainte de repornire.
Mesajele JSON invalide sau cu câmpuri de bază incorecte sunt ignorate și afișate ca erori.
Exemplul este pentru demonstrație locală: nu include reconectare automată sau confirmare de recepție la client.

## Surse

- https://docs.python.org/3.12/library/socket.html
- https://docs.python.org/3.12/library/threading.html
- https://docs.python.org/3.12/library/json.html
