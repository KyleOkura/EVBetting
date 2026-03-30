import { useEffect, useState } from 'react';
import axios from 'axios';
import type { Bet, SettledTotals } from '../types';
import BetTable from '../components/BetTable';

export default function SettledBets() {
  const [bets, setBets] = useState<Bet[]>([]);
  const [totals, setTotals] = useState<SettledTotals | null>(null);

  function load() {
    axios.get<{ bets: Bet[]; totals: SettledTotals }>('/api/settled_bets').then(r => {
      setBets(r.data.bets);
      setTotals(r.data.totals);
    });
  }

  useEffect(load, []);

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-100 mb-5">Settled Bets</h1>
      <BetTable
        bets={bets}
        showNet
        totalEV={totals?.total_ev}
        totalNet={totals?.total_net}
        betsWon={totals?.bets_won}
        betsLost={totals?.bets_lost}
        onRefresh={load}
      />
    </div>
  );
}
