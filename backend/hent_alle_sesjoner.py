# ============================================================
# STORTINGSVOTERING - HENT ALLE SESJONER
# ============================================================
# Dette scriptet henter voteringsdata for ALLE sesjoner
# fra 2011-2012 til i dag. 
#
# ⚠️  VIKTIG: Dette tar LANG tid (flere timer)!
#     For testing, bruk maks_saker_per_sesjon=5
# ============================================================

from hent_data import samle_voteringsdata, hent_fra_api
import json
import os
from datetime import datetime

# ============================================================
# ALLE TILGJENGELIGE SESJONER
# ============================================================
# Stortingets API har data tilbake til 2011-2012

ALLE_SESJONER = [
    "2011-2012",  # Stoltenberg II (Ap-Sp-SV)
    "2012-2013",  # Stoltenberg II → Solberg I
    "2013-2014",  # Solberg I (H-FrP, støtte fra V-KrF)
    "2014-2015",  # Solberg I
    "2015-2016",  # Solberg I
    "2016-2017",  # Solberg I
    "2017-2018",  # Solberg I → Solberg II (H-FrP-V)
    "2018-2019",  # Solberg II → Solberg III (H-FrP-V-KrF)
    "2019-2020",  # Solberg III → Solberg IV (H-V-KrF, FrP ut)
    "2020-2021",  # Solberg IV
    "2021-2022",  # Støre I (Ap-Sp)
    "2022-2023",  # Støre I
    "2023-2024",  # Støre I
    "2024-2025",  # Støre I (pågående)
]


def hent_alle_sesjoner(fra_sesjon=None, til_sesjon=None, maks_saker_per_sesjon=None):
    """
    Henter voteringsdata for flere sesjoner.
    
    Parametre:
        fra_sesjon: Start fra denne sesjonen (f.eks. "2017-2018")
        til_sesjon: Stopp etter denne sesjonen
        maks_saker_per_sesjon: Begrens antall saker (for testing)
    
    Eksempler:
        # Hent alt fra 2017 til nå
        hent_alle_sesjoner(fra_sesjon="2017-2018")
        
        # Hent bare 2020-2023
        hent_alle_sesjoner(fra_sesjon="2020-2021", til_sesjon="2022-2023")
        
        # Test med 5 saker per sesjon
        hent_alle_sesjoner(maks_saker_per_sesjon=5)
    """
    print("\n" + "="*60)
    print("🚀 HENTER DATA FOR FLERE SESJONER")
    print("="*60)
    
    # Bestem hvilke sesjoner som skal hentes
    sesjoner = ALLE_SESJONER.copy()
    
    if fra_sesjon:
        try:
            fra_idx = sesjoner.index(fra_sesjon)
            sesjoner = sesjoner[fra_idx:]
        except ValueError:
            print(f"⚠️  Ukjent sesjon: {fra_sesjon}")
            print(f"   Gyldige sesjoner: {', '.join(ALLE_SESJONER)}")
            return None
    
    if til_sesjon:
        try:
            til_idx = sesjoner.index(til_sesjon)
            sesjoner = sesjoner[:til_idx + 1]
        except ValueError:
            print(f"⚠️  Ukjent sesjon: {til_sesjon}")
            return None
    
    print(f"\n📅 Vil hente {len(sesjoner)} sesjoner:")
    for s in sesjoner:
        print(f"   • {s}")
    
    if maks_saker_per_sesjon:
        print(f"\n⚠️  Begrenset til {maks_saker_per_sesjon} saker per sesjon (testmodus)")
    
    # Estimer tid
    if maks_saker_per_sesjon:
        estimert_min = len(sesjoner) * maks_saker_per_sesjon * 0.5
    else:
        estimert_min = len(sesjoner) * 30  # Ca. 30 min per sesjon
    
    print(f"\n⏱️  Estimert tid: {estimert_min:.0f}-{estimert_min*2:.0f} minutter")
    print("   (Avhenger av antall voteringer per sesjon)")
    
    input("\nTrykk ENTER for å starte, eller Ctrl+C for å avbryte...")
    
    # Hent hver sesjon
    resultater = {}
    start_total = datetime.now()
    
    for i, sesjon in enumerate(sesjoner):
        print(f"\n{'='*60}")
        print(f"📦 SESJON {i+1}/{len(sesjoner)}: {sesjon}")
        print(f"{'='*60}")
        
        try:
            data = samle_voteringsdata(
                sesjon_id=sesjon,
                maks_saker=maks_saker_per_sesjon,
                lagre_til_fil=True
            )
            
            resultater[sesjon] = {
                "status": "ok",
                "antall_voteringer": data["antall_voteringer"],
                "antall_saker": data["antall_saker"]
            }
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Avbrutt av bruker!")
            break
        except Exception as e:
            print(f"❌ Feil: {e}")
            resultater[sesjon] = {
                "status": "feil",
                "feilmelding": str(e)
            }
    
    # Oppsummering
    slutt_total = datetime.now()
    total_tid = (slutt_total - start_total).total_seconds() / 60
    
    print("\n" + "="*60)
    print("📊 OPPSUMMERING")
    print("="*60)
    
    totalt_voteringer = 0
    
    for sesjon, res in resultater.items():
        if res["status"] == "ok":
            totalt_voteringer += res["antall_voteringer"]
            print(f"   ✅ {sesjon}: {res['antall_voteringer']} voteringer")
        else:
            print(f"   ❌ {sesjon}: {res['feilmelding']}")
    
    print(f"\n   Totalt: {totalt_voteringer} voteringer")
    print(f"   Tid brukt: {total_tid:.1f} minutter")
    
    # Lagre oversikt
    oversikt = {
        "hentet_dato": datetime.now().isoformat(),
        "sesjoner": resultater,
        "totalt_voteringer": totalt_voteringer
    }
    
    os.makedirs("../data", exist_ok=True)
    with open("../data/oversikt_sesjoner.json", "w", encoding="utf-8") as f:
        json.dump(oversikt, f, ensure_ascii=False, indent=2)
    
    print(f"\n   💾 Oversikt lagret til data/oversikt_sesjoner.json")
    
    return resultater


# ============================================================
# KJØR
# ============================================================

if __name__ == "__main__":
    print("""
🏛️  Stortingsvotering - Hent alle sesjoner
============================================

Dette scriptet henter voteringsdata for alle sesjoner fra 2011.

ALTERNATIVER:

1. Hent ALT (tar flere timer):
   python hent_alle_sesjoner.py

2. Fra Python - hent fra 2017:
   from hent_alle_sesjoner import hent_alle_sesjoner
   hent_alle_sesjoner(fra_sesjon="2017-2018")

3. For testing (5 saker per sesjon):
   from hent_alle_sesjoner import hent_alle_sesjoner
   hent_alle_sesjoner(maks_saker_per_sesjon=5)

""")
    
    # Kommenter inn for å kjøre:
    # hent_alle_sesjoner()
