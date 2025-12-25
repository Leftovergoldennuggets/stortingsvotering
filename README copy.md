# 🇳🇴 Stortingsvotering

**Se hvordan partiene på Stortinget stemmer**

Et åpent demokratiprosjekt som visualiserer voteringsdata fra Stortinget. 
Se hvilke partier som er enige, hvem som samarbeider, og hvordan de stemmer over tid.

---

## 📁 Prosjektstruktur

```
stortingsvotering/
├── backend/                    # Python-kode for datahenting og analyse
│   ├── hent_data.py           # Henter data fra Stortingets API
│   └── analyser_data.py       # Analyserer partisamarbeid
├── frontend/                   # Nettside (React)
│   └── Stortingsvotering.jsx  # Hovedkomponenten
├── data/                       # Lagrede data (JSON-filer)
│   └── analyse_2023-2024.json # Eksempeldata
└── README.md                   # Denne filen
```

---

## 🚀 Kom i gang

### Steg 1: Installer Python-avhengigheter

```bash
# Du trenger bare "requests" biblioteket
pip install requests
```

### Steg 2: Hent data fra Stortinget

```bash
cd backend

# Åpne Python og kjør:
python3
>>> from hent_data import samle_voteringsdata
>>> data = samle_voteringsdata(sesjon_id="2023-2024", maks_saker=50)
```

**OBS:** Dette kan ta 10-30 minutter avhengig av hvor mange saker du henter.
Start med `maks_saker=10` for testing.

### Steg 3: Analyser dataene

```python
>>> from analyser_data import analyser_sesjon
>>> resultater = analyser_sesjon("2023-2024")
```

Dette lager en `analyse_2023-2024.json` fil i `data/`-mappen.

### Steg 4: Start nettsiden (lokal utvikling)

For å kjøre frontend lokalt, kan du bruke Vite eller Next.js.

**Med Vite:**
```bash
# I en ny mappe, sett opp Vite med React
npm create vite@latest stortingsvotering-web -- --template react
cd stortingsvotering-web
npm install

# Kopier Stortingsvotering.jsx til src/
# Oppdater App.jsx til å bruke komponenten
npm run dev
```

---

## 🌐 Hosting med Vercel

### Oppsett for produksjon

1. **Opprett et GitHub-repo** og push koden din

2. **Koble til Vercel:**
   - Gå til [vercel.com](https://vercel.com)
   - "New Project" → Importer fra GitHub
   - Velg "Vite" som framework
   - Deploy!

3. **For automatisk oppdatering av data:**
   - Bruk Vercel Cron Jobs eller GitHub Actions
   - Kjør datahenting daglig/ukentlig

### Estimerte kostnader

| Tjeneste | Kostnad |
|----------|---------|
| Vercel (hosting) | $0 (gratis tier) |
| Supabase (database) | $0 (gratis tier) |
| Domene (.no) | ~150 kr/år |
| **Total per måned** | **~$1-2** |

---

## 📊 Hvordan dataene hentes

### API-flyt

```
1. SESJONER
   https://data.stortinget.no/eksport/stortingsperioder
   └── Gir oss: 2023-2024, 2022-2023, etc.

2. SAKER (per sesjon)
   https://data.stortinget.no/eksport/saker?sesjonid=2023-2024
   └── Gir oss: Lovforslag, budsjett, spørsmål, etc.

3. VOTERINGER (per sak)
   https://data.stortinget.no/eksport/voteringer?sakid=12345
   └── Gir oss: Antall for/mot, om vedtatt, etc.

4. VOTERINGSRESULTAT (per votering)
   https://data.stortinget.no/eksport/voteringsresultat?voteringid=7523
   └── Gir oss: Hver representants stemme med parti!
```

### Analyse-algoritme

For å beregne partisamarbeid:

1. **For hver votering:** Finn hva hvert parti stemte (flertallet i partiet)
2. **For hvert par av partier:** Tell hvor ofte de stemte likt
3. **Beregn prosent:** `enighet = (antall_likt / totalt) * 100`

---

## 🎨 Funksjonalitet

### Implementert ✅
- [x] Hente partier fra Stortingets API
- [x] Hente saker og voteringer
- [x] Hente individuelle stemmer
- [x] Beregne parti-enighetsmatrise
- [x] Finne mest/minst enige partipar
- [x] Interaktiv nettside med visualisering

### Planlagt 📋
- [ ] Tidsserie: Enighet over tid
- [ ] Filtrering på sakstype (budsjett, lov, etc.)
- [ ] Enkeltrepresentanter som bryter partilinjen
- [ ] Sammenligning mellom sesjoner
- [ ] Søk i saker

---

## 📚 Ressurser

- **Stortingets API:** https://data.stortinget.no
- **API-dokumentasjon:** https://data.stortinget.no/dokumentasjon-og-hjelp/
- **Bruksvilkår:** Gratis, men oppgi Stortinget som kilde

---

## 🤝 Bidra

Dette er et åpent prosjekt! Bidrag er velkomne:

1. Fork repoet
2. Lag en branch (`git checkout -b feature/ny-funksjon`)
3. Commit endringer (`git commit -m 'Legger til ny funksjon'`)
4. Push (`git push origin feature/ny-funksjon`)
5. Åpne en Pull Request

---

## 📄 Lisens

MIT License - bruk fritt!

---

*Laget med ❤️ for åpenhet i det norske demokratiet*
