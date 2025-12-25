# Metodikk: Stortingsvotering-analyse

> Dette dokumentet forklarer nøyaktig hvordan alle beregninger gjøres.
> Full transparens er avgjørende for at journalister og andre skal kunne stole på dataene.

---

## 📥 Datakilde

**All data hentes fra Stortingets offisielle API:**
- Nettsted: https://data.stortinget.no/
- Lisens: Åpne data, gratis tilgjengelig for alle
- Krav: Stortinget skal oppgis som kilde

Data oppdateres av Stortinget kort tid etter hvert møte. Vår database synkroniseres [daglig/ukentlig].

---

## 📊 Definisjoner og beregninger

### 1. Partistandpunkt i en votering

For hver votering bestemmes partiets standpunkt slik:

```
1. Tell antall representanter fra partiet som stemte FOR
2. Tell antall representanter fra partiet som stemte MOT
3. Partiets standpunkt = det flertallet stemte
```

**Eksempel fra ekte data:**

| Parti | Stemte FOR | Stemte MOT | Fravær | → Standpunkt |
|-------|------------|------------|--------|--------------|
| Arbeiderpartiet | 45 | 0 | 3 | FOR |
| Høyre | 2 | 34 | 2 | MOT |
| SV | 13 | 0 | 0 | FOR |
| FrP | 0 | 21 | 0 | MOT |

**Spesialtilfeller:**

| Situasjon | Håndtering |
|-----------|------------|
| Like mange FOR og MOT | Markeres som "DELT", utelates fra enighetsberegning |
| Alle fraværende | Partiet utelates fra denne voteringen |
| Kun én representant | Telles normalt (den ene stemmen bestemmer) |

---

### 2. Enighet mellom to partier

**Definisjon:**

| Parti A | Parti B | Resultat |
|---------|---------|----------|
| FOR | FOR | ✅ ENIGE |
| MOT | MOT | ✅ ENIGE |
| FOR | MOT | ❌ UENIGE |
| MOT | FOR | ❌ UENIGE |

**Viktig:** Vi sammenligner partistandpunkt, ikke individuelle stemmer.

---

### 3. Enighetsprosent

Formelen for enighetsprosent mellom parti A og parti B:

```
                    antall voteringer der A og B var ENIGE
enighet_prosent = ------------------------------------------ × 100
                    antall voteringer der begge deltok
```

**Eksempel:**

- Ap og Sp deltok begge i 832 voteringer
- De var enige i 742 av dem
- Enighet: (742 / 832) × 100 = **89.2%**

---

### 4. "På vinnersiden"

En måling av hvor ofte partiet stemte med flertallet:

```
                        voteringer der partiet stemte som flertallet
vinnerside_prosent = ------------------------------------------------- × 100
                        voteringer der partiet deltok
```

Regjeringspartier har typisk høy "vinnerside"-prosent fordi de har flertall.

---

## ⚠️ Begrensninger og forbehold

### Datahistorikk
Stortingets API inneholder kun voteringsdata fra sesjonen **2011-2012 og fremover**. Eldre data er ikke tilgjengelig digitalt.

### Partipisking
De aller fleste voteringer på Stortinget er "partipisket" – partiet stemmer samlet. Dette betyr at enkeltrepresentanter som bryter med partilinjen er sjeldne, men de forekommer.

### Fravær
Representanter som var fraværende telles ikke i beregningene. Et parti med høyt fravær i en periode kan få skjev statistikk.

### Hva vi IKKE måler
- Intensitet i uenighet (et "nei" til en liten detalj teller likt som "nei" til hele lovforslaget)
- Retorikk og debatt
- Forhandlinger bak kulissene
- Komitéarbeid før votering

---

## 🔍 Slik kan du verifisere

### Metode 1: Stortingets egen side

1. Gå til [stortinget.no](https://www.stortinget.no)
2. Søk opp en sak
3. Klikk "Votering" for å se hvordan hver representant stemte
4. Sammenlign med våre tall

### Metode 2: Kjør koden selv

```bash
# Klon repoet
git clone [repo-url]

# Installer avhengigheter
pip install requests

# Kjør verifisering
python backend/verifiser_data.py
```

### Metode 3: Last ned rådata

Alle voteringer vi har analysert er tilgjengelige som JSON-filer i `data/`-mappen. Du kan inspisere dem direkte.

---

## 📝 Eksempel: Fullstendig sporbarhet

For å vise hvordan én datapunkt kan spores tilbake til kilden:

**Påstand:** "Ap og Sp var enige i 89.2% av voteringene i 2023-2024"

**Verifisering:**

1. **Rådata finnes i:** `data/voteringer_2023-2024.json`

2. **Eksempel-votering der de var enige:**
   - Votering ID: 17648
   - Sak: Statsbudsjettet 2024
   - Ap stemte: FOR (45-0)
   - Sp stemte: FOR (28-0)
   - Stortingets side: `https://www.stortinget.no/.../votering/17648`

3. **Eksempel-votering der de var uenige:**
   - Votering ID: 17892
   - Sak: [saksnavn]
   - Ap stemte: FOR
   - Sp stemte: MOT
   - Stortingets side: `https://www.stortinget.no/.../votering/17892`

4. **Total beregning:**
   - 832 voteringer der begge deltok
   - 742 ganger enige
   - 742 / 832 = 0.892 = 89.2%

---

## 🛡️ Kvalitetssikring

Vi gjør følgende for å sikre datakvalitet:

1. **Automatisk validering** ved datahenting (sjekker at API-respons er gyldig)
2. **Stikkprøvekontroll** av tilfeldige voteringer mot Stortingets nettside
3. **Åpen kildekode** slik at alle kan inspisere logikken
4. **Versjonskontroll** av alle endringer i koden

---

## 📧 Feil eller spørsmål?

Finner du feil i dataene eller har spørsmål om metodikken?

- Åpne en issue på GitHub
- Send e-post til [e-postadresse]

Vi tar feil på alvor og vil rette dem så raskt som mulig.

---

*Sist oppdatert: [dato]*
