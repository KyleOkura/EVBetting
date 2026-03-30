import { useEffect, useState } from 'react';
import axios from 'axios';
import type { EVBet } from '../types';

interface TakeBetForm {
  bet: EVBet;
  bookie: string;
  amount: string;
  date: string;
  bonus: boolean;
}

export default function SelectBets() {
  const [bets, setBets] = useState<EVBet[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [modal, setModal] = useState<TakeBetForm | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function load() {
    setLoading(true);
    axios.get<{ bets: EVBet[] }>('/api/select_bets').then(r => {
      setBets(r.data.bets);
      setLoading(false);
    });
  }

  useEffect(load, []);

  async function refresh() {
    setRefreshing(true);
    const r = await axios.post<{ bets: EVBet[] }>('/api/refresh_bets');
    setBets(r.data.bets);
    setRefreshing(false);
  }

  function openModal(bet: EVBet) {
    setModal({
      bet,
      bookie: bet.bookies[0] ?? '',
      amount: String(Math.round(bet.kelly_wager)),
      date: new Date().toISOString().split('T')[0],
      bonus: false,
    });
  }

  async function takeBet() {
    if (!modal) return;
    setSubmitting(true);
    await axios.post('/api/take_bet', {
      bet_id: modal.bet.bet_id,
      sport: modal.bet.sport,
      team: modal.bet.team,
      bookie: modal.bookie,
      odds: modal.bet.odds,
      amount: modal.amount,
      ev: modal.bet.bet_EV,
      date: modal.date,
      bonus_bet: modal.bonus,
    });
    setSubmitting(false);
    setModal(null);
    load();
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-xl font-bold text-gray-100">Available EV Bets</h1>
        <button
          onClick={refresh}
          disabled={refreshing}
          className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium disabled:opacity-50"
        >
          {refreshing ? 'Refreshing…' : 'Refresh Bets'}
        </button>
      </div>

      {loading ? (
        <p className="text-gray-400 text-sm">Loading…</p>
      ) : bets.length === 0 ? (
        <p className="text-gray-400 text-sm">No EV bets available. Click Refresh Bets to fetch the latest.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-gray-700">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-800 text-gray-400 text-xs uppercase tracking-wider">
                <th className="px-3 py-2 text-left">Team</th>
                <th className="px-3 py-2 text-left">Sport</th>
                <th className="px-3 py-2 text-left">Bookies</th>
                <th className="px-3 py-2 text-right">Odds</th>
                <th className="px-3 py-2 text-right">EV%</th>
                <th className="px-3 py-2 text-right">Kelly%</th>
                <th className="px-3 py-2 text-right">Kelly Wager</th>
                <th className="px-3 py-2 text-left">Date</th>
                <th className="px-3 py-2"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {bets.map(bet => (
                <tr key={bet.bet_id} className="hover:bg-gray-800/50 transition-colors">
                  <td className="px-3 py-2 text-gray-100 font-medium max-w-[160px] truncate">{bet.team}</td>
                  <td className="px-3 py-2 text-gray-400">{bet.sport}</td>
                  <td className="px-3 py-2 text-gray-300 text-xs">{bet.bookies.join(', ')}</td>
                  <td className="px-3 py-2 text-right text-gray-200">
                    {bet.odds > 0 ? `+${bet.odds}` : bet.odds}
                  </td>
                  <td className="px-3 py-2 text-right text-emerald-400">{bet.bet_EV}%</td>
                  <td className="px-3 py-2 text-right text-gray-300">{bet.kelly_percent}%</td>
                  <td className="px-3 py-2 text-right text-gray-200">${bet.kelly_wager}</td>
                  <td className="px-3 py-2 text-gray-400">{bet.date}</td>
                  <td className="px-3 py-2">
                    <button
                      onClick={() => openModal(bet)}
                      className="px-3 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium"
                    >
                      Take Bet
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Take Bet Modal */}
      {modal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setModal(null)}>
          <div
            className="bg-gray-800 rounded-xl p-6 w-full max-w-md shadow-2xl border border-gray-700"
            onClick={e => e.stopPropagation()}
          >
            <h2 className="text-lg font-semibold mb-4 text-gray-100">Take Bet</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-200 font-medium">{modal.bet.team}</p>
                <p className="text-xs text-gray-400">{modal.bet.sport} — {modal.bet.odds > 0 ? '+' : ''}{modal.bet.odds}</p>
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">Bookie</label>
                <select
                  value={modal.bookie}
                  onChange={e => setModal({ ...modal, bookie: e.target.value })}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm text-gray-100"
                >
                  {modal.bet.bookies.map(b => <option key={b} value={b}>{b}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">Bet Amount ($)</label>
                <input
                  type="number"
                  step="any"
                  value={modal.amount}
                  onChange={e => setModal({ ...modal, amount: e.target.value })}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm text-gray-100"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">Date</label>
                <input
                  type="date"
                  value={modal.date}
                  onChange={e => setModal({ ...modal, date: e.target.value })}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm text-gray-100"
                />
              </div>
              <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={modal.bonus}
                  onChange={e => setModal({ ...modal, bonus: e.target.checked })}
                  className="rounded"
                />
                Bonus Bet
              </label>
            </div>
            <div className="mt-5 flex justify-between">
              <button
                onClick={takeBet}
                disabled={submitting}
                className="px-4 py-2 rounded text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50"
              >
                {submitting ? 'Placing…' : 'Place Bet'}
              </button>
              <button onClick={() => setModal(null)} className="px-4 py-2 text-sm text-gray-400 hover:text-gray-200">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
