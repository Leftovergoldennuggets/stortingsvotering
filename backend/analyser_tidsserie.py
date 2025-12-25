# ============================================================
# STORTINGSVOTERING - ANALYSER OVER TID
# ============================================================
# Dette scriptet analyserer hvordan partienighet har endret seg
# over tid, fra 2011 til i dag.
#
# Perfekt for å se:
# - Hvordan regjeringsskifter påvirker samarbeidsmønstre
# - Hvilke partier som har nærmet seg / fjernet seg
# - Trender i norsk politikk
# ============================================================

import json
import os
from collections import defaultdict
from analyser_data import analyser_sesjon

# ============================================================
# HOVEDFUNKSJON
# ============================================================

def analyser_alle_sesjoner(data_mappe="../data"):
    """
    Analyserer alle sesjoner og lager en tidsserie.
    
    Forventer at du allerede har hentet data med hent_alle_sesjoner.py
    
    Returnerer:
        Dictionary med:
        - tidsserie: Enighet per partipar per sesjon
        - gjennomsnitt: Gjennomsnittlig enighet per partipar
    """
    print("="*60)
    print("📈 ANALYSERER PARTIENIGHET OVER TID")
    print("="*60)
    
    # Finn alle votering-filer
    filer = sorted([
        f for f in os.listdir(data_mappe) 
        if f.startswith("voteringer_") and f.endswith(".json")
    ])
    
    if not filer:
        print("❌ Fant ingen votering-filer!")
        print(f"   Kjør først: python hent_alle_sesjoner.py")
        return None
    
    print(f"\n📂 Fant {len(filer)} sesjoner å analysere")
    
    # Analyser hver sesjon
    alle_analyser = {}
    
    for fil in filer:
        # Hent sesjon-ID fra filnavnet (f.eks. "voteringer_2023-2024.json")
        sesjon_id = fil.replace("voteringer_", "").replace(".json", "")
        
        print(f"\n   Analyserer {sesjon_id}...")
        
        try:
            analyse = analyser_sesjon(sesjon_id, data_mappe=data_mappe)
            alle_analyser[sesjon_id] = analyse
            print(f"   ✓ {analyse['antall_voteringer']} voteringer")
        except Exception as e:
            print(f"   ⚠️  Feil: {e}")
    
    # Bygg tidsserie for hvert partipar
    print("\n📊 Bygger tidsserie...")
    
    tidsserie = defaultdict(dict)
    alle_partipar = set()
    
    for sesjon_id, analyse in alle_analyser.items():
        enighetsmatrise = analyse.get("enighetsmatrise", {})
        
        for parti_a, partnere in enighetsmatrise.items():
            for parti_b, prosent in partnere.items():
                if parti_a < parti_b:  # Unngå duplikater
                    partipar = f"{parti_a}-{parti_b}"
                    tidsserie[partipar][sesjon_id] = prosent
                    alle_partipar.add(partipar)
    
    # Beregn gjennomsnitt per partipar
    gjennomsnitt = {}
    for partipar, sesjoner in tidsserie.items():
        verdier = list(sesjoner.values())
        gjennomsnitt[partipar] = round(sum(verdier) / len(verdier), 1)
    
    # Finn interessante trender
    print("\n🔍 Interessante funn:")
    print("-" * 50)
    
    # Hvem har nærmet seg mest?
    endringer = []
    for partipar, sesjoner in tidsserie.items():
        sorterte = sorted(sesjoner.items())
        if len(sorterte) >= 2:
            første = sorterte[0][1]
            siste = sorterte[-1][1]
            endring = siste - første
            endringer.append((partipar, endring, første, siste))
    
    endringer.sort(key=lambda x: x[1], reverse=True)
    
    print("\n   📈 Nærmet seg mest:")
    for partipar, endring, før, etter in endringer[:3]:
        print(f"      {partipar}: {før:.0f}% → {etter:.0f}% (+{endring:.0f})")
    
    print("\n   📉 Fjernet seg mest:")
    for partipar, endring, før, etter in endringer[-3:]:
        print(f"      {partipar}: {før:.0f}% → {etter:.0f}% ({endring:.0f})")
    
    # Mest stabile
    stabile = []
    for partipar, sesjoner in tidsserie.items():
        verdier = list(sesjoner.values())
        if len(verdier) >= 3:
            variasjon = max(verdier) - min(verdier)
            stabile.append((partipar, variasjon, gjennomsnitt[partipar]))
    
    stabile.sort(key=lambda x: x[1])
    
    print("\n   🎯 Mest stabile samarbeid:")
    for partipar, var, snitt in stabile[:3]:
        print(f"      {partipar}: {snitt:.0f}% (±{var/2:.0f}%)")
    
    # Lagre resultater
    resultat = {
        "analysert_dato": datetime.now().isoformat() if 'datetime' in dir() else None,
        "antall_sesjoner": len(alle_analyser),
        "tidsserie": dict(tidsserie),
        "gjennomsnitt": gjennomsnitt,
        "sesjonsanalyser": {
            sesjon: {
                "antall_voteringer": a["antall_voteringer"],
                "mest_enige": a.get("mest_enige", [])[:3],
                "minst_enige": a.get("minst_enige", [])[:3]
            }
            for sesjon, a in alle_analyser.items()
        }
    }
    
    # Lagre til fil
    output_fil = f"{data_mappe}/analyse_tidsserie.json"
    with open(output_fil, "w", encoding="utf-8") as f:
        json.dump(resultat, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Resultat lagret til {output_fil}")
    
    return resultat


def lag_tidsserie_for_frontend(data_mappe="../data"):
    """
    Lager en forenklet tidsserie-fil optimalisert for frontend.
    
    Formatet er enkelt å bruke i React/JavaScript.
    """
    print("\n📦 Lager frontend-data...")
    
    # Les analyse_tidsserie.json
    try:
        with open(f"{data_mappe}/analyse_tidsserie.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("   Kjører full analyse først...")
        data = analyser_alle_sesjoner(data_mappe)
    
    if not data:
        return None
    
    # Konverter til frontend-vennlig format
    sesjoner = sorted(set(
        sesjon 
        for partipar_data in data["tidsserie"].values() 
        for sesjon in partipar_data.keys()
    ))
    
    # For hvert partipar, lag en dataserie
    dataserier = []
    
    for partipar, sesjon_data in data["tidsserie"].items():
        parti_a, parti_b = partipar.split("-")
        
        datapunkter = [
            {
                "sesjon": sesjon,
                "år": int(sesjon.split("-")[0]),
                "enighet": sesjon_data.get(sesjon)
            }
            for sesjon in sesjoner
        ]
        
        dataserier.append({
            "partipar": partipar,
            "parti_a": parti_a,
            "parti_b": parti_b,
            "gjennomsnitt": data["gjennomsnitt"].get(partipar),
            "data": datapunkter
        })
    
    # Sorter etter gjennomsnittlig enighet
    dataserier.sort(key=lambda x: x["gjennomsnitt"] or 0, reverse=True)
    
    frontend_data = {
        "sesjoner": sesjoner,
        "dataserier": dataserier,
        "metadata": {
            "antall_sesjoner": len(sesjoner),
            "antall_partipar": len(dataserier),
            "periode": f"{sesjoner[0]} til {sesjoner[-1]}" if sesjoner else ""
        }
    }
    
    # Lagre
    output_fil = f"{data_mappe}/tidsserie_frontend.json"
    with open(output_fil, "w", encoding="utf-8") as f:
        json.dump(frontend_data, f, ensure_ascii=False, indent=2)
    
    print(f"   ✓ Lagret til {output_fil}")
    
    return frontend_data


# ============================================================
# KJØR
# ============================================================

if __name__ == "__main__":
    from datetime import datetime
    
    print("""
📈 Stortingsvotering - Tidsserieanalyse
=======================================

Dette scriptet analyserer hvordan partienighet har endret seg over tid.

FORUTSETNING:
Kjør først hent_alle_sesjoner.py for å laste ned data.

BRUK:
    python analyser_tidsserie.py

""")
    
    # Kjør analyse
    resultat = analyser_alle_sesjoner()
    
    if resultat:
        # Lag også frontend-data
        lag_tidsserie_for_frontend()
        
        print("\n✅ Ferdig!")
        print("   Nå kan du bruke tidsserie_frontend.json i React-appen.")
