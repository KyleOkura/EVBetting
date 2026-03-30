import { useEffect, useState } from 'react';
import axios from 'axios';
import type { Bet } from '../types';
import BetTable from '../components/BetTable';

export default function AllBets() {
  const [bets, setBets] = useState<Bet[]>([]);

  function load() {
    axios.get<{ bets: Bet[] }>('/api/all_bets').then(r => setBets(r.data.bets));
  }

  useEffect(load, []);

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-100 mb-5">All Bets</h1>
      <BetTable bets={bets} showNet onRefresh={load} />
    </div>
  );
}
