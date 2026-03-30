import { useEffect, useState } from 'react';
import axios from 'axios';
import type { Bet } from '../types';
import BetTable from '../components/BetTable';

export default function CurrentBets() {
  const [bets, setBets] = useState<Bet[]>([]);
  const [totalEV, setTotalEV] = useState(0);
  const [totalWagered, setTotalWagered] = useState(0);

  function load() {
    axios.get<{ bets: Bet[]; total_ev: number; total_wagered: number }>('/api/current_bets').then(r => {
      setBets(r.data.bets);
      setTotalEV(r.data.total_ev);
      setTotalWagered(r.data.total_wagered);
    });
  }

  useEffect(load, []);

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-100 mb-5">Pending Bets</h1>
      <BetTable
        bets={bets}
        totalEV={totalEV}
        totalWagered={totalWagered}
        onRefresh={load}
      />
    </div>
  );
}
