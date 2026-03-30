import { useEffect, useState } from 'react';
import axios from 'axios';

const BOOKIE_LOGOS: Record<string, string> = {
  draftkings: '/draftkings.png',
  fanduel: '/fanduel.jpg',
  betmgm: '/betmgm2.png',
  betrivers: '/betrivers.png',
  ballybet: '/ballybet.png',
  espnbet: '/espnbet.png',
  fanatics: '/fanatics.png',
  williamhill_us: '/caesars.webp',
};

const BOOKIE_LABELS: Record<string, string> = {
  draftkings: 'DraftKings',
  fanduel: 'FanDuel',
  betmgm: 'BetMGM',
  betrivers: 'BetRivers',
  ballybet: 'BallyBet',
  espnbet: 'ESPN Bet',
  fanatics: 'Fanatics',
  williamhill_us: "Caesars",
};

interface HomeData {
  net: number;
  bookie_nets: Record<string, number>;
}

export default function Home() {
  const [data, setData] = useState<HomeData | null>(null);

  useEffect(() => {
    axios.get<HomeData>('/api/home').then(r => setData(r.data));
  }, []);

  if (!data) {
    return <div className="text-gray-400 text-sm">Loading…</div>;
  }

  const { net, bookie_nets } = data;

  return (
    <div>
      <div className="mb-6 flex items-center gap-4">
        <img src="/evbetlogo.png" alt="EVBet" className="w-14 h-14" />
        <div>
          <h1 className="text-2xl font-bold text-gray-100">EVBetting Dashboard</h1>
          <p className="text-sm text-gray-400">Total net across all books</p>
        </div>
      </div>

      {/* Overall net */}
      <div className={`inline-block rounded-xl px-6 py-4 mb-8 text-3xl font-bold border ${net >= 0 ? 'bg-blue-950 border-blue-700 text-blue-300' : 'bg-red-950 border-red-700 text-red-300'}`}>
        {net >= 0 ? '+' : ''}${net.toFixed(2)}
      </div>

      {/* Per-bookie grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {Object.entries(bookie_nets).map(([name, bookieNet]) => (
          <div key={name} className="bg-gray-800 rounded-xl p-4 border border-gray-700 flex flex-col items-center gap-2">
            {BOOKIE_LOGOS[name] && (
              <img src={BOOKIE_LOGOS[name]} alt={name} className="h-8 w-auto object-contain" />
            )}
            <p className="text-xs text-gray-400 uppercase tracking-wide">{BOOKIE_LABELS[name] ?? name}</p>
            <p className={`text-xl font-semibold ${bookieNet >= 0 ? 'text-blue-400' : 'text-red-400'}`}>
              {bookieNet >= 0 ? '+' : ''}${bookieNet.toFixed(2)}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
