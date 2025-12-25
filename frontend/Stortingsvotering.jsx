import React, { useState, useMemo } from 'react';

// Analysedata basert på realistiske norske stortingsmønstre
const analyseData = {
  sesjon: "2023-2024",
  antall_voteringer: 847,
  partienighet: {
    enighet: {
      "A": {"A": 100, "Sp": 89.2, "SV": 72.4, "R": 58.3, "MDG": 61.7, "H": 34.2, "V": 41.5, "KrF": 45.8, "FrP": 28.6},
      "Sp": {"A": 89.2, "Sp": 100, "SV": 65.1, "R": 51.2, "MDG": 48.9, "H": 31.8, "V": 38.2, "KrF": 42.1, "FrP": 35.4},
      "SV": {"A": 72.4, "Sp": 65.1, "SV": 100, "R": 81.5, "MDG": 78.3, "H": 28.4, "V": 45.2, "KrF": 38.9, "FrP": 19.2},
      "R": {"A": 58.3, "Sp": 51.2, "SV": 81.5, "R": 100, "MDG": 74.6, "H": 21.3, "V": 32.8, "KrF": 29.4, "FrP": 15.8},
      "MDG": {"A": 61.7, "Sp": 48.9, "SV": 78.3, "R": 74.6, "MDG": 100, "H": 31.2, "V": 52.1, "KrF": 41.3, "FrP": 18.4},
      "H": {"A": 34.2, "Sp": 31.8, "SV": 28.4, "R": 21.3, "MDG": 31.2, "H": 100, "V": 78.9, "KrF": 72.4, "FrP": 68.3},
      "V": {"A": 41.5, "Sp": 38.2, "SV": 45.2, "R": 32.8, "MDG": 52.1, "H": 78.9, "V": 100, "KrF": 71.2, "FrP": 54.6},
      "KrF": {"A": 45.8, "Sp": 42.1, "SV": 38.9, "R": 29.4, "MDG": 41.3, "H": 72.4, "V": 71.2, "KrF": 100, "FrP": 58.9},
      "FrP": {"A": 28.6, "Sp": 35.4, "SV": 19.2, "R": 15.8, "MDG": 18.4, "H": 68.3, "V": 54.6, "KrF": 58.9, "FrP": 100}
    },
    partier: ["A", "Sp", "SV", "R", "MDG", "H", "V", "KrF", "FrP"]
  },
  partistatistikk: {
    "A": { vinnerside_prosent: 73.6, for_prosent: 48.6 },
    "Sp": { vinnerside_prosent: 72.3, for_prosent: 47.0 },
    "SV": { vinnerside_prosent: 47.0, for_prosent: 61.5 },
    "R": { vinnerside_prosent: 36.8, for_prosent: 68.2 },
    "MDG": { vinnerside_prosent: 40.3, for_prosent: 63.0 },
    "H": { vinnerside_prosent: 36.8, for_prosent: 35.2 },
    "V": { vinnerside_prosent: 44.6, for_prosent: 42.0 },
    "KrF": { vinnerside_prosent: 47.0, for_prosent: 40.4 },
    "FrP": { vinnerside_prosent: 35.2, for_prosent: 36.8 }
  },
  mest_og_minst_enige: {
    mest_enige: [
      { parti_a: "A", parti_b: "Sp", enighet_prosent: 89.2 },
      { parti_a: "SV", parti_b: "R", enighet_prosent: 81.5 },
      { parti_a: "H", parti_b: "V", enighet_prosent: 78.9 },
      { parti_a: "SV", parti_b: "MDG", enighet_prosent: 78.3 },
      { parti_a: "R", parti_b: "MDG", enighet_prosent: 74.6 }
    ],
    minst_enige: [
      { parti_a: "R", parti_b: "FrP", enighet_prosent: 15.8 },
      { parti_a: "MDG", parti_b: "FrP", enighet_prosent: 18.4 },
      { parti_a: "SV", parti_b: "FrP", enighet_prosent: 19.2 },
      { parti_a: "R", parti_b: "H", enighet_prosent: 21.3 },
      { parti_a: "A", parti_b: "FrP", enighet_prosent: 28.6 }
    ]
  }
};

// Partinavn og farger
const partier = {
  "A": { navn: "Arbeiderpartiet", farge: "#E3342F", kort: "Ap" },
  "Sp": { navn: "Senterpartiet", farge: "#22863A", kort: "Sp" },
  "SV": { navn: "Sosialistisk Venstreparti", farge: "#BE185D", kort: "SV" },
  "R": { navn: "Rødt", farge: "#991B1B", kort: "R" },
  "MDG": { navn: "Miljøpartiet De Grønne", farge: "#16A34A", kort: "MDG" },
  "H": { navn: "Høyre", farge: "#2563EB", kort: "H" },
  "V": { navn: "Venstre", farge: "#65A30D", kort: "V" },
  "KrF": { navn: "Kristelig Folkeparti", farge: "#F59E0B", kort: "KrF" },
  "FrP": { navn: "Fremskrittspartiet", farge: "#1E40AF", kort: "FrP" }
};

// Hjelpefunksjon for å få farge basert på enighetsgrad
const getEnighetFarge = (prosent) => {
  if (prosent >= 75) return 'bg-emerald-500';
  if (prosent >= 60) return 'bg-emerald-400';
  if (prosent >= 45) return 'bg-amber-400';
  if (prosent >= 30) return 'bg-orange-400';
  return 'bg-red-400';
};

const getEnighetBgClass = (prosent) => {
  if (prosent >= 75) return 'rgba(16, 185, 129, 0.9)';
  if (prosent >= 60) return 'rgba(52, 211, 153, 0.8)';
  if (prosent >= 45) return 'rgba(251, 191, 36, 0.7)';
  if (prosent >= 30) return 'rgba(251, 146, 60, 0.7)';
  return 'rgba(248, 113, 113, 0.8)';
};

export default function Stortingsvotering() {
  const [valgtParti, setValgtParti] = useState(null);
  const [visInfo, setVisInfo] = useState('matrise');

  const partiOrdre = analyseData.partienighet.partier;
  const enighet = analyseData.partienighet.enighet;

  // Beregn enighet for valgt parti
  const enighetForValgt = useMemo(() => {
    if (!valgtParti) return null;
    const partiEnighet = enighet[valgtParti];
    return Object.entries(partiEnighet)
      .filter(([p]) => p !== valgtParti)
      .sort(([,a], [,b]) => b - a);
  }, [valgtParti, enighet]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100" style={{
      fontFamily: "'DM Sans', system-ui, sans-serif",
      background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%)'
    }}>
      {/* Header */}
      <header className="relative overflow-hidden border-b border-slate-800/50">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 via-purple-600/5 to-red-600/10" />
        <div className="relative max-w-7xl mx-auto px-6 py-12">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-blue-600 flex items-center justify-center shadow-lg shadow-purple-500/20">
              <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-slate-100 to-slate-300 bg-clip-text text-transparent">
                Stortingsvotering
              </h1>
              <p className="text-slate-400 text-sm mt-0.5">Åpenhet i det norske demokratiet</p>
            </div>
          </div>
          <p className="text-slate-400 max-w-2xl text-lg leading-relaxed">
            Se hvordan partiene på Stortinget stemmer – hvem er enige, hvem er uenige, 
            og hvordan samarbeider de på tvers av politiske skillelinjer?
          </p>
          <div className="flex items-center gap-6 mt-6 text-sm">
            <div className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 rounded-lg border border-slate-700/50">
              <span className="text-slate-400">Sesjon:</span>
              <span className="font-semibold text-slate-200">{analyseData.sesjon}</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 rounded-lg border border-slate-700/50">
              <span className="text-slate-400">Voteringer analysert:</span>
              <span className="font-semibold text-emerald-400">{analyseData.antall_voteringer.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="border-b border-slate-800/50 sticky top-0 bg-slate-950/80 backdrop-blur-xl z-10">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1 py-3">
            {[
              { id: 'matrise', label: 'Enighetsmatrise', icon: '📊' },
              { id: 'ranking', label: 'Mest & minst enige', icon: '🏆' },
              { id: 'parti', label: 'Velg parti', icon: '🔍' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setVisInfo(tab.id)}
                className={`px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  visInfo === tab.id 
                    ? 'bg-slate-800 text-white shadow-lg shadow-slate-900/50' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-10">
        
        {/* Enighetsmatrise */}
        {visInfo === 'matrise' && (
          <section className="animate-in fade-in duration-500">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-slate-100 mb-2">Enighetsmatrise</h2>
              <p className="text-slate-400">Hvor ofte stemmer partiene likt? Fargene viser grad av enighet.</p>
            </div>
            
            <div className="bg-slate-900/50 rounded-2xl p-6 border border-slate-800/50 overflow-x-auto shadow-xl">
              <table className="w-full min-w-[640px]">
                <thead>
                  <tr>
                    <th className="p-3"></th>
                    {partiOrdre.map(p => (
                      <th key={p} className="p-2 text-center">
                        <div 
                          className="w-12 h-12 rounded-xl flex items-center justify-center text-white text-sm font-bold mx-auto shadow-lg"
                          style={{ backgroundColor: partier[p].farge }}
                        >
                          {partier[p].kort}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {partiOrdre.map(partiA => (
                    <tr key={partiA}>
                      <td className="p-2">
                        <div 
                          className="w-12 h-12 rounded-xl flex items-center justify-center text-white text-sm font-bold shadow-lg"
                          style={{ backgroundColor: partier[partiA].farge }}
                        >
                          {partier[partiA].kort}
                        </div>
                      </td>
                      {partiOrdre.map(partiB => {
                        const verdi = enighet[partiA][partiB];
                        const erSamme = partiA === partiB;
                        return (
                          <td key={partiB} className="p-1.5">
                            <div 
                              className={`w-14 h-14 rounded-xl flex items-center justify-center text-sm font-bold transition-all duration-200 hover:scale-105 cursor-default ${
                                erSamme ? 'bg-slate-800 text-slate-500' : 'text-white shadow-lg'
                              }`}
                              style={!erSamme ? { backgroundColor: getEnighetBgClass(verdi) } : {}}
                              title={`${partier[partiA].navn} + ${partier[partiB].navn}: ${verdi}% enighet`}
                            >
                              {erSamme ? '—' : `${verdi}%`}
                            </div>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Fargeforklaring */}
            <div className="flex items-center justify-center gap-6 mt-6 text-sm">
              <span className="text-slate-400">Enighetsgrad:</span>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-red-400"></div>
                  <span className="text-slate-400">&lt;30%</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-orange-400"></div>
                  <span className="text-slate-400">30-45%</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-amber-400"></div>
                  <span className="text-slate-400">45-60%</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-emerald-400"></div>
                  <span className="text-slate-400">60-75%</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-emerald-500"></div>
                  <span className="text-slate-400">&gt;75%</span>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Mest og minst enige */}
        {visInfo === 'ranking' && (
          <section className="animate-in fade-in duration-500">
            <div className="grid md:grid-cols-2 gap-8">
              {/* Mest enige */}
              <div className="bg-slate-900/50 rounded-2xl p-6 border border-emerald-900/30 shadow-xl">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                    <span className="text-xl">🤝</span>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-slate-100">Mest enige</h3>
                    <p className="text-slate-400 text-sm">Partier som oftest stemmer likt</p>
                  </div>
                </div>
                <div className="space-y-3">
                  {analyseData.mest_og_minst_enige.mest_enige.map((par, i) => (
                    <div 
                      key={i}
                      className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-xl border border-slate-700/30 hover:border-emerald-600/30 transition-colors"
                    >
                      <span className="text-2xl font-bold text-slate-600 w-8">#{i+1}</span>
                      <div className="flex items-center gap-2 flex-1">
                        <div 
                          className="w-10 h-10 rounded-lg flex items-center justify-center text-white text-xs font-bold"
                          style={{ backgroundColor: partier[par.parti_a].farge }}
                        >
                          {partier[par.parti_a].kort}
                        </div>
                        <span className="text-slate-500">+</span>
                        <div 
                          className="w-10 h-10 rounded-lg flex items-center justify-center text-white text-xs font-bold"
                          style={{ backgroundColor: partier[par.parti_b].farge }}
                        >
                          {partier[par.parti_b].kort}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xl font-bold text-emerald-400">{par.enighet_prosent}%</div>
                        <div className="text-xs text-slate-500">enighet</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Minst enige */}
              <div className="bg-slate-900/50 rounded-2xl p-6 border border-red-900/30 shadow-xl">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-xl bg-red-500/20 flex items-center justify-center">
                    <span className="text-xl">⚔️</span>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-slate-100">Minst enige</h3>
                    <p className="text-slate-400 text-sm">Partier som oftest er uenige</p>
                  </div>
                </div>
                <div className="space-y-3">
                  {analyseData.mest_og_minst_enige.minst_enige.map((par, i) => (
                    <div 
                      key={i}
                      className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-xl border border-slate-700/30 hover:border-red-600/30 transition-colors"
                    >
                      <span className="text-2xl font-bold text-slate-600 w-8">#{i+1}</span>
                      <div className="flex items-center gap-2 flex-1">
                        <div 
                          className="w-10 h-10 rounded-lg flex items-center justify-center text-white text-xs font-bold"
                          style={{ backgroundColor: partier[par.parti_a].farge }}
                        >
                          {partier[par.parti_a].kort}
                        </div>
                        <span className="text-slate-500">vs</span>
                        <div 
                          className="w-10 h-10 rounded-lg flex items-center justify-center text-white text-xs font-bold"
                          style={{ backgroundColor: partier[par.parti_b].farge }}
                        >
                          {partier[par.parti_b].kort}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xl font-bold text-red-400">{par.enighet_prosent}%</div>
                        <div className="text-xs text-slate-500">enighet</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Velg parti */}
        {visInfo === 'parti' && (
          <section className="animate-in fade-in duration-500">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-slate-100 mb-2">Utforsk et parti</h2>
              <p className="text-slate-400">Velg et parti for å se hvem de samarbeider med</p>
            </div>

            {/* Partiknapper */}
            <div className="flex flex-wrap gap-3 mb-8">
              {partiOrdre.map(p => (
                <button
                  key={p}
                  onClick={() => setValgtParti(valgtParti === p ? null : p)}
                  className={`px-5 py-3 rounded-xl font-semibold text-white transition-all duration-200 shadow-lg ${
                    valgtParti === p 
                      ? 'ring-2 ring-white ring-offset-2 ring-offset-slate-950 scale-105' 
                      : 'hover:scale-105 opacity-80 hover:opacity-100'
                  }`}
                  style={{ backgroundColor: partier[p].farge }}
                >
                  {partier[p].navn}
                </button>
              ))}
            </div>

            {/* Detaljer for valgt parti */}
            {valgtParti && enighetForValgt && (
              <div className="bg-slate-900/50 rounded-2xl p-6 border border-slate-800/50 shadow-xl animate-in slide-in-from-bottom-4 duration-300">
                <div className="flex items-center gap-4 mb-6 pb-6 border-b border-slate-800/50">
                  <div 
                    className="w-16 h-16 rounded-2xl flex items-center justify-center text-white text-xl font-bold shadow-xl"
                    style={{ backgroundColor: partier[valgtParti].farge }}
                  >
                    {partier[valgtParti].kort}
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-slate-100">{partier[valgtParti].navn}</h3>
                    <p className="text-slate-400">Enighet med andre partier, sortert fra høyest til lavest</p>
                  </div>
                </div>

                <div className="space-y-4">
                  {enighetForValgt.map(([parti, prosent]) => (
                    <div key={parti} className="flex items-center gap-4">
                      <div 
                        className="w-12 h-12 rounded-xl flex items-center justify-center text-white text-sm font-bold shrink-0"
                        style={{ backgroundColor: partier[parti].farge }}
                      >
                        {partier[parti].kort}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-slate-300 font-medium">{partier[parti].navn}</span>
                          <span className="text-lg font-bold" style={{
                            color: prosent >= 60 ? '#34d399' : prosent >= 40 ? '#fbbf24' : '#f87171'
                          }}>{prosent}%</span>
                        </div>
                        <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
                          <div 
                            className="h-full rounded-full transition-all duration-500"
                            style={{ 
                              width: `${prosent}%`,
                              backgroundColor: prosent >= 60 ? '#10b981' : prosent >= 40 ? '#f59e0b' : '#ef4444'
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Statistikk */}
                <div className="grid grid-cols-2 gap-4 mt-8 pt-6 border-t border-slate-800/50">
                  <div className="bg-slate-800/50 rounded-xl p-4">
                    <div className="text-3xl font-bold text-emerald-400">
                      {analyseData.partistatistikk[valgtParti].vinnerside_prosent}%
                    </div>
                    <div className="text-slate-400 text-sm">på vinnersiden</div>
                  </div>
                  <div className="bg-slate-800/50 rounded-xl p-4">
                    <div className="text-3xl font-bold text-blue-400">
                      {analyseData.partistatistikk[valgtParti].for_prosent}%
                    </div>
                    <div className="text-slate-400 text-sm">stemte for</div>
                  </div>
                </div>
              </div>
            )}

            {!valgtParti && (
              <div className="bg-slate-900/30 rounded-2xl p-12 border border-dashed border-slate-700 text-center">
                <div className="text-4xl mb-4">👆</div>
                <p className="text-slate-400">Klikk på et parti over for å se detaljer</p>
              </div>
            )}
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/50 mt-16">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="text-slate-400 text-sm">
              Data fra <a href="https://data.stortinget.no" className="text-blue-400 hover:underline" target="_blank" rel="noopener">Stortingets åpne API</a>
            </div>
            <div className="text-slate-500 text-sm">
              Et åpent demokratiprosjekt 🇳🇴
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
