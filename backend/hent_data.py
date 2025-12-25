# ============================================================
# STORTINGSVOTERING - DATAHENTING
# ============================================================
# Dette scriptet henter voteringsdata fra Stortingets åpne API.
# API-dokumentasjon: https://data.stortinget.no/
# ============================================================

# --- IMPORTERER BIBLIOTEKER ---
# "requests" lar oss hente data fra internett (som en nettleser)
import requests

# "json" lar oss jobbe med JSON-data (et vanlig dataformat)
import json

# "time" lar oss legge inn pauser (for å ikke overbelaste API-et)
import time

# "os" lar oss jobbe med filer og mapper
import os

# "datetime" lar oss jobbe med datoer
from datetime import datetime


# ============================================================
# KONFIGURASJON
# ============================================================
# Her definerer vi grunnleggende innstillinger for scriptet.
# Du kan endre disse verdiene etter behov.

# Basis-URL for Stortingets API
API_BASE_URL = "https://data.stortinget.no/eksport"

# Hvor lang pause mellom API-kall (i sekunder)
# Stortinget tillater 100 kall per minutt, så 0.7 sekunder er trygt
PAUSE_MELLOM_KALL = 0.7

# Hvilken sesjon vi skal hente data fra
# Format: "ÅÅÅÅ-ÅÅÅÅ" (f.eks. "2023-2024")
STANDARD_SESJON = "2023-2024"


# ============================================================
# HJELPEFUNKSJONER
# ============================================================
# Disse små funksjonene gjør spesifikke oppgaver og brukes
# av hovedfunksjonene lenger ned.

def hent_fra_api(endpoint, parametre=None):
    """
    Henter data fra Stortingets API.
    
    Parametre:
        endpoint: Hvilken del av API-et vi skal hente fra (f.eks. "partier")
        parametre: Ekstra søkeparametre som en dictionary
    
    Returnerer:
        Dictionary med data fra API-et, eller None hvis det feiler
    
    Eksempel:
        data = hent_fra_api("partier", {"sesjonid": "2023-2024"})
    """
    # Bygger opp den fulle URL-en
    url = f"{API_BASE_URL}/{endpoint}"
    
    # Legger til format=json så vi får JSON tilbake (ikke XML)
    if parametre is None:
        parametre = {}
    parametre["format"] = "json"
    
    try:
        # Sender forespørselen til Stortingets server
        # "timeout=30" betyr at vi venter maks 30 sekunder på svar
        respons = requests.get(url, params=parametre, timeout=30)
        
        # Sjekker om forespørselen var vellykket (statuskode 200 = OK)
        if respons.status_code == 200:
            # Konverterer JSON-teksten til en Python-dictionary
            return respons.json()
        else:
            # Hvis noe gikk galt, skriv ut feilmelding
            print(f"Feil ved henting fra {url}: Status {respons.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        # Hvis det oppstår en nettverksfeil
        print(f"Nettverksfeil ved henting fra {url}: {e}")
        return None


def lagre_til_json(data, filnavn):
    """
    Lagrer data til en JSON-fil.
    
    Parametre:
        data: Dataen som skal lagres (dictionary eller liste)
        filnavn: Navnet på filen (f.eks. "partier.json")
    
    Eksempel:
        lagre_til_json(mine_data, "data/partier.json")
    """
    # Finner mappen der dette scriptet ligger
    script_mappe = os.path.dirname(os.path.abspath(__file__))
    
    # Går én mappe opp og inn i "data"-mappen
    data_mappe = os.path.join(script_mappe, "..", "data")
    
    # Lager data-mappen hvis den ikke finnes
    os.makedirs(data_mappe, exist_ok=True)
    
    # Full sti til filen
    fil_sti = os.path.join(data_mappe, filnavn)
    
    # Åpner filen og skriver dataen
    # "ensure_ascii=False" sørger for at norske tegn (æøå) vises riktig
    # "indent=2" gjør filen lettere å lese for mennesker
    with open(fil_sti, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Lagret data til {filnavn}")


def les_fra_json(filnavn):
    """
    Leser data fra en JSON-fil.
    
    Parametre:
        filnavn: Navnet på filen som skal leses
    
    Returnerer:
        Dataen fra filen, eller None hvis filen ikke finnes
    """
    script_mappe = os.path.dirname(os.path.abspath(__file__))
    data_mappe = os.path.join(script_mappe, "..", "data")
    fil_sti = os.path.join(data_mappe, filnavn)
    
    # Sjekker om filen finnes
    if not os.path.exists(fil_sti):
        print(f"Filen {filnavn} finnes ikke")
        return None
    
    # Leser og returnerer dataen
    with open(fil_sti, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# HOVEDFUNKSJONER FOR DATAHENTING
# ============================================================
# Disse funksjonene henter spesifikke typer data fra API-et.

def hent_partier(sesjon_id=STANDARD_SESJON):
    """
    Henter liste over alle partier på Stortinget for en gitt sesjon.
    
    Returnerer en liste med partier, hver med:
        - id: Partiforkortelse (f.eks. "H", "A", "Sp")
        - navn: Fullt partinavn (f.eks. "Høyre", "Arbeiderpartiet")
    """
    print(f"\n📋 Henter partier for sesjon {sesjon_id}...")
    
    data = hent_fra_api("partier", {"sesjonid": sesjon_id})
    
    if data and "partier_liste" in data:
        partier = data["partier_liste"]
        print(f"   Fant {len(partier)} partier")
        return partier
    
    return []


def hent_saker(sesjon_id=STANDARD_SESJON):
    """
    Henter alle saker behandlet i Stortinget for en gitt sesjon.
    
    En "sak" kan være et lovforslag, budsjettvedtak, interpellasjon, etc.
    
    Returnerer en liste med saker, hver med:
        - id: Unik sak-ID
        - tittel: Beskrivelse av saken
        - sakstype: Type sak (lovforslag, budsjett, etc.)
    """
    print(f"\n📁 Henter saker for sesjon {sesjon_id}...")
    
    data = hent_fra_api("saker", {"sesjonid": sesjon_id})
    
    if data and "saker_liste" in data:
        saker = data["saker_liste"]
        print(f"   Fant {len(saker)} saker")
        return saker
    
    return []


def hent_voteringer_for_sak(sak_id):
    """
    Henter alle voteringer (avstemninger) for en spesifikk sak.
    
    Én sak kan ha flere voteringer, f.eks. én for hvert forslag.
    
    Parametre:
        sak_id: ID-en til saken vi vil hente voteringer for
    
    Returnerer en liste med voteringer, hver med:
        - votering_id: Unik votering-ID
        - antall_for: Antall som stemte for
        - antall_mot: Antall som stemte mot
        - vedtatt: True/False om forslaget ble vedtatt
    """
    data = hent_fra_api("voteringer", {"sakid": sak_id})
    
    if data and "sak_votering_liste" in data:
        return data["sak_votering_liste"]
    
    return []


def hent_voteringsresultat(votering_id):
    """
    Henter detaljert resultat for én votering - hvem stemte hva.
    
    Dette er kjernedata for å analysere partisamarbeid!
    
    Parametre:
        votering_id: ID-en til voteringen
    
    Returnerer en liste med stemmer, hver med:
        - representant: Info om representanten (navn, parti, fylke)
        - votering: "for", "mot", eller "ikke_tilstede"
    """
    data = hent_fra_api("voteringsresultat", {"voteringid": votering_id})
    
    if data and "voteringsresultat_liste" in data:
        return data["voteringsresultat_liste"]
    
    return []


# ============================================================
# FUNKSJONER FOR DATAINNSAMLING
# ============================================================
# Disse funksjonene koordinerer innsamlingen av data.

def samle_voteringsdata(sesjon_id=STANDARD_SESJON, maks_saker=50):
    """
    Samler inn voteringsdata for en hel sesjon.
    
    Denne funksjonen:
    1. Henter alle saker i sesjonen
    2. For hver sak, henter alle voteringer
    3. For hver votering, henter hvordan hver representant stemte
    4. Lagrer alt til JSON-filer
    
    Parametre:
        sesjon_id: Hvilken sesjon vi henter fra
        maks_saker: Maks antall saker å behandle (for testing)
    
    OBS: Dette kan ta lang tid! Med 100+ saker og pauser mellom
    hvert API-kall kan det ta 30-60 minutter for en hel sesjon.
    """
    print("=" * 60)
    print(f"STARTER DATAINNSAMLING FOR SESJON {sesjon_id}")
    print("=" * 60)
    
    # Steg 1: Hent partier
    partier = hent_partier(sesjon_id)
    if partier:
        lagre_til_json(partier, f"partier_{sesjon_id}.json")
    
    # Steg 2: Hent saker
    alle_saker = hent_saker(sesjon_id)
    
    # Begrenser antall saker for testing
    saker_å_behandle = alle_saker[:maks_saker]
    print(f"\n🔄 Behandler {len(saker_å_behandle)} av {len(alle_saker)} saker...")
    
    # Her samler vi all voteringsdata
    all_voteringsdata = []
    
    # Steg 3: Gå gjennom hver sak
    for i, sak in enumerate(saker_å_behandle):
        sak_id = sak.get("id")
        sak_tittel = sak.get("tittel", "Ukjent")[:50]  # Korter ned lange titler
        
        print(f"\n[{i+1}/{len(saker_å_behandle)}] Sak {sak_id}: {sak_tittel}...")
        
        # Hent voteringer for denne saken
        time.sleep(PAUSE_MELLOM_KALL)  # Pause for å ikke overbelaste API-et
        voteringer = hent_voteringer_for_sak(sak_id)
        
        if not voteringer:
            print(f"   Ingen voteringer for denne saken")
            continue
        
        print(f"   Fant {len(voteringer)} votering(er)")
        
        # Steg 4: For hver votering, hent detaljert resultat
        for votering in voteringer:
            votering_id = votering.get("votering_id")
            
            if not votering_id:
                continue
            
            time.sleep(PAUSE_MELLOM_KALL)
            stemmer = hent_voteringsresultat(votering_id)
            
            if stemmer:
                # Lagrer voteringen med all info
                votering_med_detaljer = {
                    "sak_id": sak_id,
                    "sak_tittel": sak.get("tittel"),
                    "sakstype": sak.get("sakstype"),
                    "votering_id": votering_id,
                    "votering_tema": votering.get("votering_tema"),
                    "antall_for": votering.get("antall_for"),
                    "antall_mot": votering.get("antall_mot"),
                    "vedtatt": votering.get("vedtatt"),
                    "dato": votering.get("votering_tid"),
                    "stemmer": stemmer
                }
                all_voteringsdata.append(votering_med_detaljer)
    
    # Steg 5: Lagre all data
    print(f"\n💾 Lagrer {len(all_voteringsdata)} voteringer...")
    lagre_til_json(all_voteringsdata, f"voteringer_{sesjon_id}.json")
    
    print("\n" + "=" * 60)
    print("✅ DATAINNSAMLING FULLFØRT!")
    print("=" * 60)
    
    return all_voteringsdata


# ============================================================
# KJØR SCRIPTET
# ============================================================
# Denne delen kjører når du kjører filen direkte.

if __name__ == "__main__":
    # Eksempel: Hent data for noen saker (for testing)
    # Endre maks_saker til et høyere tall for mer data
    
    print("\n🚀 Stortingsvotering - Datahenting")
    print("=" * 40)
    print("Dette scriptet henter voteringsdata fra Stortinget.")
    print("Det kan ta litt tid avhengig av hvor mye data du henter.")
    print("=" * 40)
    
    # Start datainnsamling (10 saker for demo)
    # data = samle_voteringsdata(sesjon_id="2023-2024", maks_saker=10)
    
    # For å kjøre: fjern "#" foran linjen over, eller kjør:
    # python hent_data.py
    
    print("\n📝 For å starte datainnsamling, kjør:")
    print("   from hent_data import samle_voteringsdata")
    print("   data = samle_voteringsdata(maks_saker=10)")
