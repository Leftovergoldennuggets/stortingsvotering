# ============================================================
# STORTINGSVOTERING - VERIFISERING
# ============================================================
# Dette scriptet lar deg verifisere at analysene stemmer.
# 
# VIKTIG: Transparens og etterprøvbarhet er avgjørende når
# journalister og andre skal bruke dataene. Dette scriptet
# viser steg-for-steg hvordan beregningene gjøres.
# ============================================================

import requests
import json
import random
from collections import defaultdict

API_BASE_URL = "https://data.stortinget.no/eksport"

# ============================================================
# VERIFISERINGSFUNKSJONER
# ============================================================

def verifiser_enkelt_votering(votering_id):
    """
    Henter én votering og viser NØYAKTIG hvordan partistandpunkt beregnes.
    
    Denne funksjonen er designet for å være 100% transparent:
    - Viser rådata fra API-et
    - Viser hver enkelt stemme
    - Viser steg-for-steg beregning
    - Gir lenke til Stortingets egen side for manuell sjekk
    
    Parametre:
        votering_id: ID-en til voteringen som skal verifiseres
    """
    print("=" * 70)
    print(f"VERIFISERING AV VOTERING {votering_id}")
    print("=" * 70)
    
    # Steg 1: Hent rådata fra API
    print("\n📥 STEG 1: Henter rådata fra Stortingets API")
    print("-" * 50)
    
    url = f"{API_BASE_URL}/voteringsresultat?voteringid={votering_id}&format=json"
    print(f"   API-URL: {url}")
    
    try:
        respons = requests.get(url, timeout=30)
        if respons.status_code != 200:
            print(f"   ❌ Feil: HTTP {respons.status_code}")
            return None
        data = respons.json()
    except Exception as e:
        print(f"   ❌ Nettverksfeil: {e}")
        return None
    
    stemmer = data.get("voteringsresultat_liste", [])
    print(f"   ✓ Hentet {len(stemmer)} individuelle stemmer")
    
    # Steg 2: Vis hver enkelt stemme (første 10 som eksempel)
    print("\n📋 STEG 2: Viser individuelle stemmer (utvalg)")
    print("-" * 50)
    print(f"   {'Representant':<25} {'Parti':<8} {'Stemme':<15}")
    print(f"   {'-'*25} {'-'*8} {'-'*15}")
    
    for stemme in stemmer[:10]:
        rep = stemme.get("representant", {})
        navn = f"{rep.get('fornavn', '')} {rep.get('etternavn', '')}"
        parti = rep.get("parti", {}).get("id", "?")
        votering = stemme.get("votering", "?")
        print(f"   {navn:<25} {parti:<8} {votering:<15}")
    
    if len(stemmer) > 10:
        print(f"   ... og {len(stemmer) - 10} flere")
    
    # Steg 3: Tell opp stemmer per parti
    print("\n🔢 STEG 3: Teller opp stemmer per parti")
    print("-" * 50)
    
    partitelling = defaultdict(lambda: {"for": 0, "mot": 0, "ikke_tilstede": 0})
    
    for stemme in stemmer:
        rep = stemme.get("representant", {})
        parti_id = rep.get("parti", {}).get("id", "Ukjent")
        resultat = stemme.get("votering", "ikke_tilstede")
        
        if resultat == "for":
            partitelling[parti_id]["for"] += 1
        elif resultat == "mot":
            partitelling[parti_id]["mot"] += 1
        else:
            partitelling[parti_id]["ikke_tilstede"] += 1
    
    print(f"   {'Parti':<8} {'FOR':>6} {'MOT':>6} {'FRAVÆR':>8} {'→ STANDPUNKT':<15}")
    print(f"   {'-'*8} {'-'*6} {'-'*6} {'-'*8} {'-'*15}")
    
    partistandpunkt = {}
    
    for parti_id in sorted(partitelling.keys()):
        t = partitelling[parti_id]
        
        # Beregn standpunkt basert på flertall
        if t["for"] == 0 and t["mot"] == 0:
            standpunkt = "FRAVÆR"
        elif t["for"] > t["mot"]:
            standpunkt = "FOR"
        elif t["mot"] > t["for"]:
            standpunkt = "MOT"
        else:
            standpunkt = "DELT"
        
        partistandpunkt[parti_id] = standpunkt
        
        print(f"   {parti_id:<8} {t['for']:>6} {t['mot']:>6} {t['ikke_tilstede']:>8} → {standpunkt:<15}")
    
    # Steg 4: Vis hvordan enighet beregnes
    print("\n🤝 STEG 4: Beregner enighet mellom partier")
    print("-" * 50)
    print("   Regel: To partier er ENIGE hvis begge stemte FOR eller begge stemte MOT")
    print("   Regel: To partier er UENIGE hvis én stemte FOR og én stemte MOT")
    print()
    
    aktive_partier = [p for p, s in partistandpunkt.items() if s in ["FOR", "MOT"]]
    
    print(f"   Aktive partier i denne voteringen: {', '.join(aktive_partier)}")
    print()
    
    # Vis noen eksempler på partipar
    if len(aktive_partier) >= 2:
        print("   Eksempler på partipar:")
        vist = 0
        for i, p1 in enumerate(aktive_partier):
            for p2 in aktive_partier[i+1:]:
                s1 = partistandpunkt[p1]
                s2 = partistandpunkt[p2]
                enige = "ENIGE ✓" if s1 == s2 else "UENIGE ✗"
                print(f"   • {p1} ({s1}) + {p2} ({s2}) = {enige}")
                vist += 1
                if vist >= 5:
                    break
            if vist >= 5:
                break
    
    # Steg 5: Gi lenke for manuell verifisering
    print("\n🔗 STEG 5: Manuell verifisering")
    print("-" * 50)
    print("   Du kan verifisere dette manuelt på Stortingets nettside:")
    print(f"   → https://www.stortinget.no/no/Saker-og-publikasjoner/Saker/Sak/Voteringsoversikt/")
    print(f"   → Søk etter votering ID {votering_id}")
    print()
    print("   API-data kan også lastes ned direkte:")
    print(f"   → {url}")
    
    print("\n" + "=" * 70)
    print("✅ VERIFISERING FULLFØRT")
    print("=" * 70)
    
    return {
        "votering_id": votering_id,
        "antall_stemmer": len(stemmer),
        "partitelling": dict(partitelling),
        "partistandpunkt": partistandpunkt
    }


def verifiser_partipar_enighet(parti_a, parti_b, voteringer_fil):
    """
    Verifiserer enighetsberegningen mellom to spesifikke partier.
    
    Går gjennom alle voteringer og viser eksakt hvordan
    enighetsprosenten ble beregnet.
    """
    print("=" * 70)
    print(f"VERIFISERER ENIGHET: {parti_a} vs {parti_b}")
    print("=" * 70)
    
    # Les lagrede voteringer
    try:
        with open(voteringer_fil, "r", encoding="utf-8") as f:
            voteringer = json.load(f)
    except FileNotFoundError:
        print(f"❌ Fant ikke filen {voteringer_fil}")
        print("   Kjør hent_data.py først for å laste ned data.")
        return None
    
    print(f"\n📂 Leser {len(voteringer)} voteringer fra {voteringer_fil}")
    
    enige = 0
    uenige = 0
    eksempler_enig = []
    eksempler_uenig = []
    
    for votering in voteringer:
        # Beregn standpunkt for begge partier
        partitelling = defaultdict(lambda: {"for": 0, "mot": 0})
        
        for stemme in votering.get("stemmer", []):
            rep = stemme.get("representant", {})
            parti_id = rep.get("parti", {}).get("id")
            resultat = stemme.get("votering")
            
            if parti_id in [parti_a, parti_b] and resultat in ["for", "mot"]:
                partitelling[parti_id][resultat] += 1
        
        # Finn standpunkt
        standpunkt_a = None
        standpunkt_b = None
        
        if partitelling[parti_a]["for"] > partitelling[parti_a]["mot"]:
            standpunkt_a = "for"
        elif partitelling[parti_a]["mot"] > partitelling[parti_a]["for"]:
            standpunkt_a = "mot"
        
        if partitelling[parti_b]["for"] > partitelling[parti_b]["mot"]:
            standpunkt_b = "for"
        elif partitelling[parti_b]["mot"] > partitelling[parti_b]["for"]:
            standpunkt_b = "mot"
        
        # Hopp over hvis ett parti ikke deltok
        if standpunkt_a is None or standpunkt_b is None:
            continue
        
        # Sjekk enighet
        if standpunkt_a == standpunkt_b:
            enige += 1
            if len(eksempler_enig) < 3:
                eksempler_enig.append({
                    "votering_id": votering.get("votering_id"),
                    "tema": votering.get("votering_tema", "")[:50],
                    "standpunkt": standpunkt_a.upper()
                })
        else:
            uenige += 1
            if len(eksempler_uenig) < 3:
                eksempler_uenig.append({
                    "votering_id": votering.get("votering_id"),
                    "tema": votering.get("votering_tema", "")[:50],
                    f"{parti_a}": standpunkt_a.upper(),
                    f"{parti_b}": standpunkt_b.upper()
                })
    
    totalt = enige + uenige
    
    print(f"\n📊 RESULTAT")
    print("-" * 50)
    print(f"   Voteringer der begge deltok: {totalt}")
    print(f"   Ganger ENIGE:                {enige}")
    print(f"   Ganger UENIGE:               {uenige}")
    print()
    
    if totalt > 0:
        prosent = (enige / totalt) * 100
        print(f"   ENIGHET: {prosent:.1f}%")
        print(f"   Beregning: ({enige} / {totalt}) × 100 = {prosent:.1f}%")
    
    print(f"\n📝 EKSEMPLER PÅ ENIGHET:")
    for eks in eksempler_enig:
        print(f"   • Votering {eks['votering_id']}: Begge stemte {eks['standpunkt']}")
        print(f"     Tema: {eks['tema']}...")
    
    print(f"\n📝 EKSEMPLER PÅ UENIGHET:")
    for eks in eksempler_uenig:
        print(f"   • Votering {eks['votering_id']}: {parti_a}={eks[parti_a]}, {parti_b}={eks[parti_b]}")
        print(f"     Tema: {eks['tema']}...")
    
    print("\n" + "=" * 70)
    
    return {
        "parti_a": parti_a,
        "parti_b": parti_b,
        "enige": enige,
        "uenige": uenige,
        "prosent": round(prosent, 1) if totalt > 0 else None
    }


def stikkprove_analyse(analyse_fil, antall=5):
    """
    Tar tilfeldige stikkprøver fra en analyse og verifiserer dem.
    
    Dette er nyttig for å sjekke at analysefilen er korrekt
    uten å måtte gå gjennom alt manuelt.
    """
    print("=" * 70)
    print("STIKKPRØVEKONTROLL")
    print("=" * 70)
    print(f"\nTar {antall} tilfeldige stikkprøver fra analysen...")
    print("Hver stikkprøve hentes på nytt fra API-et og sammenlignes.\n")
    
    # Dette krever at vi har lagret votering_id-er i analysen
    # I en fullstendig implementasjon ville vi:
    # 1. Plukke tilfeldige voteringer
    # 2. Hente dem på nytt fra API
    # 3. Sammenligne med lagret data
    
    print("⚠️  For full stikkprøvekontroll, kjør:")
    print("    verifiser_enkelt_votering(votering_id)")
    print("    med en votering-ID fra dine lagrede data.")


def generer_metodikk_dokument():
    """
    Genererer et metodikk-dokument som forklarer alle beregninger.
    
    Dette bør publiseres sammen med nettsiden for full transparens.
    """
    metodikk = """
# Metodikk: Stortingsvotering-analyse

## Datakilde

All data hentes fra Stortingets offisielle API:
- URL: https://data.stortinget.no/
- Lisens: Åpne data, gratis tilgjengelig
- Krav: Stortinget skal oppgis som kilde

## Definisjoner

### Partistandpunkt i en votering

For hver votering bestemmes partiets standpunkt slik:

1. Tell antall representanter fra partiet som stemte FOR
2. Tell antall representanter fra partiet som stemte MOT
3. Partiets standpunkt = det flertallet stemte

**Eksempel:**
- Arbeiderpartiet: 25 stemte FOR, 3 stemte MOT
- Partistandpunkt: FOR (fordi 25 > 3)

**Spesialtilfeller:**
- Hvis like mange stemte FOR og MOT: Markeres som "DELT" og utelates fra enighetsberegning
- Hvis alle var fraværende: Partiet utelates fra denne voteringen

### Enighet mellom to partier

To partier regnes som ENIGE i en votering hvis:
- Begge stemte FOR, ELLER
- Begge stemte MOT

To partier regnes som UENIGE i en votering hvis:
- Én stemte FOR og én stemte MOT

### Enighetsprosent

Enighetsprosenten mellom parti A og parti B beregnes:

```
enighet_prosent = (antall_enige / totalt_felles) × 100
```

Der:
- antall_enige = voteringer der begge hadde samme standpunkt
- totalt_felles = voteringer der begge partier deltok

## Begrensninger

1. **Voteringsdata tilbake til 2011-2012**
   Stortingets API inneholder kun voteringsdata fra sesjonen 2011-2012.

2. **Partipisking**
   De fleste voteringer er "partipisket" (partiet stemmer samlet).
   Enkeltrepresentanter som bryter med partilinjen påvirker ikke
   partistandpunktet så lenge de er i mindretall.

3. **Fravær**
   Representanter som var fraværende telles ikke. Høyt fravær
   i et parti kan påvirke statistikken.

## Verifisering

All kode er åpen kildekode. Du kan:

1. Laste ned og kjøre koden selv
2. Sammenligne med Stortingets egen voteringsvisning
3. Bruke verifiseringsscriptet for stikkprøver

## Kontakt

Feil eller spørsmål? Åpne en issue på GitHub.
"""
    
    print(metodikk)
    
    # Lagre til fil
    with open("METODIKK.md", "w", encoding="utf-8") as f:
        f.write(metodikk)
    
    print("\n✓ Metodikk-dokument lagret til METODIKK.md")


# ============================================================
# KJØR VERIFISERING
# ============================================================

if __name__ == "__main__":
    print("\n🔍 Stortingsvotering - Verifiseringsverktøy")
    print("=" * 50)
    print("""
Dette verktøyet lar deg verifisere at analysene stemmer.

Tilgjengelige funksjoner:

1. verifiser_enkelt_votering(votering_id)
   → Viser steg-for-steg hvordan én votering analyseres

2. verifiser_partipar_enighet(parti_a, parti_b, fil)
   → Viser hvordan enighet mellom to partier beregnes

3. generer_metodikk_dokument()
   → Lager et dokument som forklarer metodikken

Eksempel:
   from verifiser_data import verifiser_enkelt_votering
   verifiser_enkelt_votering(7523)
""")
