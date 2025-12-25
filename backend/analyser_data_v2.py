# ============================================================
# STORTINGSVOTERING - ANALYSER DATA (FIKSET VERSJON)
# ============================================================
# Denne versjonen håndterer det faktiske dataformatet fra
# Stortingets API der votering er tall (1-5) ikke tekst.
#
# Votering-koder fra API-et:
#   1 = for
#   2 = mot  
#   3 = ikke tilstede
#   4 = avstår
#   5 = ikke avgitt stemme
# ============================================================

import json
import os
from collections import defaultdict

# ============================================================
# VOTERING-KODER
# ============================================================

VOTERING_KODER = {
    1: "for",
    2: "mot",
    3: "ikke_tilstede",
    4: "avstar",
    5: "ikke_avgitt"
}

# ============================================================
# HJELPEFUNKSJONER
# ============================================================

def les_voteringer(sesjon_id, data_mappe="../data"):
    """
    Leser voteringsdata fra JSON-fil.
    """
    filsti = os.path.join(data_mappe, f"voteringer_{sesjon_id}.json")
    
    # Prøv også uten ../ prefix
    if not os.path.exists(filsti):
        filsti = os.path.join("data", f"voteringer_{sesjon_id}.json")
    
    if not os.path.exists(filsti):
        filsti = f"voteringer_{sesjon_id}.json"
    
    with open(filsti, "r", encoding="utf-8") as f:
        return json.load(f)


def beregn_partistandpunkt(stemmer):
    """
    Beregner hvert partis standpunkt basert på individuelle stemmer.
    
    Returnerer dict: {parti_id: "for" eller "mot"}
    """
    # Tell stemmer per parti
    partitelling = defaultdict(lambda: {"for": 0, "mot": 0})
    
    for stemme in stemmer:
        # Hent representantinfo
        rep = stemme.get("representant", {})
        parti_info = rep.get("parti", {})
        parti_id = parti_info.get("id")
        
        if not parti_id:
            continue
        
        # Hent votering (kan være tall eller tekst)
        votering = stemme.get("votering")
        
        # Konverter tall til tekst hvis nødvendig
        if isinstance(votering, int):
            votering = VOTERING_KODER.get(votering, "ukjent")
        
        # Tell for/mot
        if votering == "for" or votering == 1:
            partitelling[parti_id]["for"] += 1
        elif votering == "mot" or votering == 2:
            partitelling[parti_id]["mot"] += 1
    
    # Bestem standpunkt for hvert parti
    partistandpunkt = {}
    
    for parti_id, telling in partitelling.items():
        if telling["for"] > telling["mot"]:
            partistandpunkt[parti_id] = "for"
        elif telling["mot"] > telling["for"]:
            partistandpunkt[parti_id] = "mot"
        # Hvis likt eller bare fravær, inkluderes ikke partiet
    
    return partistandpunkt


def beregn_enighetsmatrise(voteringer):
    """
    Beregner enighetsmatrise mellom alle partier.
    
    Returnerer:
        matrise: {parti_a: {parti_b: prosent, ...}, ...}
        partipar_liste: [(parti_a, parti_b, prosent), ...]
    """
    # Tell enighet/uenighet mellom alle partipar
    partipar_telling = defaultdict(lambda: {"enige": 0, "uenige": 0})
    alle_partier = set()
    
    for votering in voteringer:
        stemmer = votering.get("stemmer", [])
        
        if not stemmer:
            continue
        
        # Beregn partistandpunkt for denne voteringen
        standpunkt = beregn_partistandpunkt(stemmer)
        
        # Legg til partier vi fant
        alle_partier.update(standpunkt.keys())
        
        # Sammenlign alle partipar
        partier = list(standpunkt.keys())
        for i, parti_a in enumerate(partier):
            for parti_b in partier[i+1:]:
                # Sorter alfabetisk for konsistent nøkkel
                if parti_a > parti_b:
                    parti_a, parti_b = parti_b, parti_a
                
                nøkkel = (parti_a, parti_b)
                
                if standpunkt[parti_a] == standpunkt[parti_b]:
                    partipar_telling[nøkkel]["enige"] += 1
                else:
                    partipar_telling[nøkkel]["uenige"] += 1
    
    # Beregn prosenter
    matrise = defaultdict(dict)
    partipar_liste = []
    
    for (parti_a, parti_b), telling in partipar_telling.items():
        totalt = telling["enige"] + telling["uenige"]
        if totalt > 0:
            prosent = round((telling["enige"] / totalt) * 100, 1)
            
            # Lagre begge veier i matrisen
            matrise[parti_a][parti_b] = prosent
            matrise[parti_b][parti_a] = prosent
            
            partipar_liste.append({
                "parti_a": parti_a,
                "parti_b": parti_b,
                "enighet_prosent": prosent,
                "antall_enige": telling["enige"],
                "antall_uenige": telling["uenige"],
                "antall_totalt": totalt
            })
    
    return dict(matrise), partipar_liste


def beregn_partistatistikk(voteringer):
    """
    Beregner statistikk for hvert parti.
    """
    partistat = defaultdict(lambda: {
        "antall_for": 0,
        "antall_mot": 0,
        "antall_voteringer": 0,
        "pa_vinnersiden": 0
    })
    
    for votering in voteringer:
        stemmer = votering.get("stemmer", [])
        if not stemmer:
            continue
        
        standpunkt = beregn_partistandpunkt(stemmer)
        
        # Finn flertallsstandpunkt
        antall_for = votering.get("antall_for", 0)
        antall_mot = votering.get("antall_mot", 0)
        flertall = "for" if antall_for > antall_mot else "mot"
        
        for parti_id, parti_standpunkt in standpunkt.items():
            partistat[parti_id]["antall_voteringer"] += 1
            
            if parti_standpunkt == "for":
                partistat[parti_id]["antall_for"] += 1
            else:
                partistat[parti_id]["antall_mot"] += 1
            
            if parti_standpunkt == flertall:
                partistat[parti_id]["pa_vinnersiden"] += 1
    
    # Beregn prosenter
    resultat = {}
    for parti_id, stat in partistat.items():
        totalt = stat["antall_voteringer"]
        resultat[parti_id] = {
            "antall_voteringer": totalt,
            "antall_for": stat["antall_for"],
            "antall_mot": stat["antall_mot"],
            "for_prosent": round((stat["antall_for"] / totalt) * 100, 1) if totalt > 0 else 0,
            "vinnersiden_prosent": round((stat["pa_vinnersiden"] / totalt) * 100, 1) if totalt > 0 else 0
        }
    
    return resultat


# ============================================================
# HOVEDFUNKSJON
# ============================================================

def analyser_sesjon(sesjon_id, data_mappe="../data"):
    """
    Analyserer all voteringsdata for en sesjon.
    
    Returnerer dictionary med:
        - enighetsmatrise
        - mest_enige (topp 10)
        - minst_enige (bunn 10)
        - partistatistikk
    """
    print("=" * 60)
    print(f"📊 ANALYSERER SESJON {sesjon_id}")
    print("=" * 60)
    
    # Les data
    try:
        data = les_voteringer(sesjon_id, data_mappe)
    except FileNotFoundError:
        print(f"❌ Fant ikke voteringer_{sesjon_id}.json")
        return None
    
    voteringer = data.get("voteringer", data) if isinstance(data, dict) else data
    
    # Hvis det er en liste direkte
    if isinstance(voteringer, list) and len(voteringer) > 0 and "stemmer" not in voteringer[0]:
        # Prøv å finne voteringer i datastrukturen
        voteringer = data
    
    print(f"   📂 Lastet {len(voteringer)} voteringer")
    
    # Filtrer ut voteringer uten stemmer
    voteringer_med_stemmer = [v for v in voteringer if v.get("stemmer")]
    print(f"   ✓ {len(voteringer_med_stemmer)} voteringer har stemmedata")
    
    if not voteringer_med_stemmer:
        print("   ❌ Ingen voteringer med stemmedata!")
        return None
    
    # Beregn enighetsmatrise
    print("   🔍 Beregner partienighet...")
    matrise, partipar_liste = beregn_enighetsmatrise(voteringer_med_stemmer)
    
    # Sorter partipar
    partipar_liste.sort(key=lambda x: x["enighet_prosent"], reverse=True)
    
    mest_enige = partipar_liste[:10]
    minst_enige = partipar_liste[-10:][::-1]  # Reverser for lavest først
    
    # Beregn partistatistikk
    print("   📈 Beregner partistatistikk...")
    partistatistikk = beregn_partistatistikk(voteringer_med_stemmer)
    
    # Lag resultat
    resultat = {
        "sesjon_id": sesjon_id,
        "antall_voteringer": len(voteringer_med_stemmer),
        "antall_partier": len(partistatistikk),
        "enighetsmatrise": matrise,
        "mest_enige": mest_enige,
        "minst_enige": minst_enige,
        "partistatistikk": partistatistikk,
        "alle_partipar": partipar_liste
    }
    
    # Lagre til fil
    output_mappe = data_mappe if os.path.exists(data_mappe) else "data"
    if not os.path.exists(output_mappe):
        output_mappe = "../data"
    
    output_fil = os.path.join(output_mappe, f"analyse_{sesjon_id}.json")
    
    with open(output_fil, "w", encoding="utf-8") as f:
        json.dump(resultat, f, ensure_ascii=False, indent=2)
    
    print(f"   💾 Lagret til {output_fil}")
    
    # Vis sammendrag
    print("\n" + "=" * 60)
    print("📋 SAMMENDRAG")
    print("=" * 60)
    
    print(f"\n🏛️  Partier funnet: {', '.join(sorted(partistatistikk.keys()))}")
    
    if mest_enige:
        print(f"\n🤝 MEST ENIGE:")
        for par in mest_enige[:5]:
            print(f"   {par['parti_a']}-{par['parti_b']}: {par['enighet_prosent']}% ({par['antall_totalt']} voteringer)")
    
    if minst_enige:
        print(f"\n⚔️  MINST ENIGE:")
        for par in minst_enige[:5]:
            print(f"   {par['parti_a']}-{par['parti_b']}: {par['enighet_prosent']}% ({par['antall_totalt']} voteringer)")
    
    print("\n" + "=" * 60)
    print("✅ ANALYSE FULLFØRT!")
    print("=" * 60)
    
    return resultat


# ============================================================
# KJØR
# ============================================================

if __name__ == "__main__":
    import sys
    
    sesjon = sys.argv[1] if len(sys.argv) > 1 else "2023-2024"
    analyser_sesjon(sesjon)
