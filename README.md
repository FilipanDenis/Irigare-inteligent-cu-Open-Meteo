# Irigare inteligentă cu Open-Meteo

**Python · MQTT · SQLite · Streamlit**

Simulare IoT pentru udarea unei grădini pe baza vremii.

**Echipa:** Filipan Cristian Denis și Oana Rareș  
**Disciplina:** Tehnici de programare în IoT (TPI)  
**Stadiu:** CP02 implementat: trei procese senzor transmit date sintetice către un gateway TCP cu thread-uri.

Codul, instrucțiunile și raportul sunt în [folderul CP02](CP02_irigare/).

## Ce face aplicația

Aplicația folosește date meteo reale pentru a decide când și cât să ude. Comparăm această metodă cu udarea zilnică la program fix.

Proiectul rulează pe laptop, fără Raspberry Pi fizic. Datele sunt transmise de un program Python care simulează un senzor. Udarea și rezerva de apă din sol sunt simulate.

## Funcționalități planificate

- [ ] Descărcarea datelor Open-Meteo pentru Baia Mare și salvarea în CSV.
- [ ] Redarea datelor prin `replay.py` și transmiterea prin MQTT / Mosquitto.
- [ ] Calcularea udării și salvarea rezultatelor în SQLite.
- [ ] Dashboard Streamlit cu vremea, deciziile și graficele.
- [ ] Model AI simplu pentru estimarea ET₀, antrenat în Google Colab.
- [ ] Agent LLM cu MCP care explică recomandările folosind datele aplicației.

ET₀ este evapotranspirația de referință: o estimare meteo a pierderii de apă prin evaporare și transpirație pentru o suprafață vegetală de referință.

## Experimentul

**Întrebare:** În ce condiții udarea bazată pe vreme economisește apă fără să crească deficitul în simulare?

| Metodă | Decizia de udare |
| --- | --- |
| Baseline: program fix | Aceeași cantitate de apă în fiecare zi. |
| Metoda propusă | Doză ajustată după rezerva estimată, ET₀ și prognoza de ploaie pentru următoarele 24 de ore. |

**Ipoteză de testat:** În scenarii cu precipitații, metoda propusă economisește cel puțin 10% apă, iar proporția zilelor cu deficit crește cu cel mult 1 punct procentual.

Testăm perioade ploioase, uscate și situații cu date lipsă sau prognoze greșite. Folosim aceleași date meteo, același model de sol și aceeași rezervă inițială. Rezerva fiecărei metode evoluează separat, după propriile udări.

Urmărim **apa totală aplicată**, **economia procentuală** și **proporția zilelor cu deficit**.

Doza fixă și pragurile se calibrează pe date separate de evaluare. Deciziile folosesc numai informații disponibile la momentul lor. Prognozele modificate artificial vor fi marcate separat.

Modelul AI va fi evaluat prin MAE, față de predicția „ET₀ mâine = ET₀ azi”.

## Instalare și rulare

Componentele vor rula ca procese separate pe laptop. Pentru demonstrarea comunicării prin rețea, le putem distribui între două calculatoare.

Dependențele, configurațiile și comenzile vor fi adăugate odată cu implementarea.

## Rezultate și limitări

Nu avem încă rezultate experimentale. Vom adăuga un tabel comparativ și grafice.

Modelul de sol este simplificat, fără măsurători fizice. Economia calculată se referă la simulare, iar ipoteza va fi verificată prin experimente.

## Surse

- [Catalogul de proiecte TPI](https://cti.ubm.ro/tpi/projects-datasets.html)
- [Exemplul de README al disciplinei](https://github.com/nucbm/TPI-greenhouse-example)
- [Documentația Open-Meteo](https://open-meteo.com/en/docs)
- [Date istorice Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api)

Date meteo: [Open-Meteo](https://open-meteo.com/), [licența CC BY 4.0](https://open-meteo.com/en/licence).
