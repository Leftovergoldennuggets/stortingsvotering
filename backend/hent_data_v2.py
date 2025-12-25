# ============================================================
# STORTINGSVOTERING - DATAHENTING (OPPDATERT)
# ============================================================
# Dette scriptet henter voteringsdata fra Stortingets åpne API.
# API-dokumentasjon: https://data.stortinget.no/
#
# ENDRINGER I DENNE VERSJONEN:
# - Økt timeout fra 30 til 60 sekunder
# - Lagt til retry-logikk (prøver 3 ganger ved feil)
# - Bedre feilhåndtering
# ============================================================

import requests
import json
import time
import os
from datetime import datetime

# ============================================================
# KONFIGURASJON
# ============================================================

API_BASE_URL = "https://data.stortinget.no/eksport"
PAUSE_MELLOM_KALL = 0.7
STANDARD_SESJON = "2023-2024"

# NYE INNSTILLINGER
TIMEOUT_SEKUNDER = 60  # Økt fra 30 til 60
MAKS_FORSØK = 3        # Antall forsøk ved feil

# ============================================================
# HJELPEFUNKSJONER
# ============================================================

def hent_fra_api(endpoint, parametre=None, forsøk=1):
    """
    Henter data fra Stortingets API med retry-logikk.
    """
    url = f"{API_BASE_URL}/{endpoint}"
    
    if parametre is None:
        parametre = {}
    parametre["format"] = "json"
    
    try:
        respons = requests.get(url, params=parametre, timeout=TIMEOUT_SEKUNDER)
        
        if respons.status_code == 200:
            return respons.json()
        else:
            print(f"   ⚠️  Feil {respons.status_code} fra {endpoint}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"   ⏱️  Timeout ved {endpoint} (forsøk {forsøk}/{MAKS_FORSØK})")
        if forsøk < MAKS_FORSØK:
            print(f"   🔄 Venter 5 sekunder og prøver igjen...")
            time.sleep(5)
            return hent_fra_api(endpoint, parametre, forsøk + 1)
        else:
            print(f"   ❌ Ga opp etter {MAKS_FORSØK} forsøk")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"   🌐 Tilkoblingsfeil ved {endpoint} (forsøk {forsøk}/{MAKS_FORSØK})")
        if forsøk < MAKS_FORSØK:
            print(f"   🔄 Venter 10 sekunder og prøver igjen...")
            time.sleep(10)
            return hent_fra_api(endpoint, parametre, forsøk + 1)
        else:
            print(f"   ❌ Ga opp etter {MAKS_FORSØK} forsøk")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Nettverksfeil: {e}")
        return None


def lagre_til_json(data, filnavn):
    """Lagrer data til en JSON-fil."""
    mappe = os.path.dirname(filnavn)
    if mappe and not os.path.exists(mappe):
        os.makedirs(mappe)
    
    with open(filnavn, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Lagret data til {filnavn}")


# ============================================================
# DATAHENTING-FUNKSJONER
# ============================================================

def hent_partier(sesjon_id):
    """Henter alle partier for en sesjon."""
    print(f"📋 Henter partier for sesjon {sesjon_id}...")
    data = hent_fra_api("partier", {"sesjonid": sesjon_id})
    
    if data and "partier_liste" in data:
        partier = data["partier_liste"]
        print(f"   ✓ Fant {len(partier)} partier")
        return partier
    return []


def hent_saker(sesjon_id):
    """Henter alle saker for en sesjon."""
    print(f"📁 Henter saker for sesjon {sesjon_id}...")
    data = hent_fra_api("saker", {"sesjonid": sesjon_id})
    
    if data and "saker_liste" in data:
        saker = data["saker_liste"]
        print(f"   ✓ Fant {len(saker)} saker")
        return saker
    return []


def hent_voteringer_for_sak(sak_id):
    """Henter alle voteringer for en sak."""
    data = hent_fra_api("voteringer", {"sakid": sak_id})
    
    if data and "votering_liste" in data:
        return data["votering_liste"]
    return []


def hent_voteringsresultat(votering_id):
    """Henter detaljert resultat for én votering."""
    data = hent_fra_api("voteringsresultat", {"voteringid": votering_id})
    
    if data and "voteringsresultat_liste" in data:
        return data["voteringsresultat_liste"]
    return []


# ============================================================
# HOVEDFUNKSJON
# ============================================================

def samle_voteringsdata(sesjon_id=None, maks_saker=None, lagre_til_fil=True):
    """
    Samler all voteringsdata for en sesjon.
    
    Parametre:
        sesjon_id: Sesjons-ID (f.eks. "2023-2024")
        maks_saker: Begrens antall saker (for testing)
        lagre_til_fil: Om resultatet skal lagres til JSON
    """
    if sesjon_id is None:
        sesjon_id = STANDARD_SESJON
    
    print("=" * 60)
    print(f"STARTER DATAINNSAMLING FOR SESJON {sesjon_id}")
    print("=" * 60)
    
    # Hent partier
    partier = hent_partier(sesjon_id)
    if partier:
        lagre_til_json(partier, f"../data/partier_{sesjon_id}.json")
    
    # Hent saker
    saker = hent_saker(sesjon_id)
    
    if not saker:
        print("❌ Kunne ikke hente saker. Sjekk internettforbindelsen.")
        return None
    
    # Begrens antall saker hvis ønskelig
    if maks_saker:
        saker = saker[:maks_saker]
        print(f"   ℹ️  Begrenset til {maks_saker} saker")
    
    # Hent voteringer for hver sak
    alle_voteringer = []
    
    print(f"\n🔄 Behandler {len(saker)} av {len(saker)} saker...")
    
    for i, sak in enumerate(saker):
        sak_id = sak.get("id")
        sak_tittel = sak.get("korttittel", "Ukjent")[:50]
        
        # Vis fremdrift
        print(f"[{i+1}/{len(saker)}] Sak {sak_id}: {sak_tittel}...")
        
        # Pause for å ikke overbelaste API-et
        time.sleep(PAUSE_MELLOM_KALL)
        
        # Hent voteringer for saken
        voteringer = hent_voteringer_for_sak(sak_id)
        
        if not voteringer:
            print(f"   Ingen voteringer for denne saken")
            continue
        
        print(f"   Fant {len(voteringer)} votering(er)")
        
        for votering in voteringer:
            votering_id = votering.get("votering_id")
            
            # Pause
            time.sleep(PAUSE_MELLOM_KALL)
            
            # Hent detaljerte stemmer
            stemmer = hent_voteringsresultat(votering_id)
            
            # Lagre voteringen med all info
            alle_voteringer.append({
                "sak_id": sak_id,
                "sak_tittel": sak.get("tittel", ""),
                "sakstype": sak.get("sakstype"),
                "votering_id": votering_id,
                "votering_tema": votering.get("votering_tema", ""),
                "antall_for": votering.get("antall_for", 0),
                "antall_mot": votering.get("antall_mot", 0),
                "vedtatt": votering.get("vedtatt", False),
                "dato": votering.get("votering_tid", ""),
                "stemmer": stemmer
            })
    
    # Lagre resultatet
    print(f"\n💾 Lagrer {len(alle_voteringer)} voteringer...")
    
    if lagre_til_fil:
        lagre_til_json(alle_voteringer, f"../data/voteringer_{sesjon_id}.json")
    
    print("=" * 60)
    print("✅ DATAINNSAMLING FULLFØRT!")
    print("=" * 60)
    
    return {
        "sesjon_id": sesjon_id,
        "antall_saker": len(saker),
        "antall_voteringer": len(alle_voteringer),
        "voteringer": alle_voteringer
    }


# ============================================================
# KJØR SCRIPTET
# ============================================================

if __name__ == "__main__":
    print("""
🚀 Stortingsvotering - Datahenting
========================================
Dette scriptet henter voteringsdata fra Stortinget.
Det kan ta litt tid avhengig av hvor mye data du henter.
========================================

📝 For å starte datainnsamling, kjør:
   from hent_data import samle_voteringsdata
   data = samle_voteringsdata(maks_saker=10)
""")
