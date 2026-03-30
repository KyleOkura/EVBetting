import { useEffect, useState } from 'react';
import axios from 'axios';
import type { Bookie, BookieTotals } from '../types';

interface StatsData {
  bookies: Bookie[];
  totals: BookieTotals;
}

interface TransferForm {
  sending: string;
  receiving: string;
  amount: string;
}

const BOOKIE_LOGOS: Record<string, string> = {
  draftkings: '/draftkings.png',
  fanduel: '/fanduel.jpg',
  betmgm: '/betmgm2.png',
  betrivers: '/betrivers.png',
  ballybet: '/ballybet.png',
  espnbet: '/espnbet.png',
  fanatics: '/fanatics.png',
  williamhill_us: '/caesars.webp',
  cash: '/cash.JPG',
};

export default function BookieStats() {
  const [data, setData] = useState<StatsData | null>(null);
  const [transferOpen, setTransferOpen] = useState(false);
  const [form, setForm] = useState<TransferForm>({ sending: '', receiving: '', amount: '' });
  const [submitting, setSubmitting] = useState(false);

  function load() {
    axios.get<StatsData>('/api/bookie_stats').then(r => {
      setData(r.data);
      if (r.data.bookies.length > 0) {
        setForm(f => ({ ...f, sending: r.data.bookies[0].bookmaker, receiving: r.data.bookies[0].bookmaker }));
      }
    });
  }

  useEffect(load, []);

  async function transfer() {
    setSubmitting(true);
    await axios.post('/api/transfer_funds', {
      sending_bookie: form.sending,
      receiving_bookie: form.receiving,
      amount: form.amount,
    });
    setSubmitting(false);
    setTransferOpen(false);
    load();
  }

  if (!data) return <p className="text-gray-400 text-sm">Loading…</p>;

  const { bookies, totals } = data;

  return (
    <div>
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-xl font-bold text-gray-100">Bookie Stats</h1>
        <button
          onClick={() => setTransferOpen(true)}
          className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium"
        >
          Transfer Funds
        </button>
      </div>

      <div className="overflow-x-auto rounded-lg border border-gray-700">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-800 text-gray-400 text-xs uppercase tracking-wider">
              <th className="px-3 py-2 text-left">Bookie</th>
              <th className="px-3 py-2 text-right">Bankroll</th>
              <th className="px-3 py-2 text-right">Wagered</th>
              <th className="px-3 py-2 text-right">Wagerable</th>
              <th className="px-3 py-2 text-right">Net Profit</th>
              <th className="px-3 py-2 text-right">Bets (P/W/L)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {bookies.map(b => (
              <tr key={b.bookmaker} className="hover:bg-gray-800/50">
                <td className="px-3 py-2">
                  <div className="flex items-center gap-2">
                    {BOOKIE_LOGOS[b.bookmaker] && (
                      <img src={BOOKIE_LOGOS[b.bookmaker]} alt={b.bookmaker} className="h-5 w-auto object-contain" />
                    )}
                    <span className="text-gray-200">{b.bookmaker}</span>
                  </div>
                </td>
                <td className="px-3 py-2 text-right text-gray-200">${b.total_bankroll.toFixed(2)}</td>
                <td className="px-3 py-2 text-right text-gray-300">${b.currently_wagered.toFixed(2)}</td>
                <td className="px-3 py-2 text-right text-gray-300">${b.wagerable.toFixed(2)}</td>
                <td className={`px-3 py-2 text-right font-medium ${b.current_net >= 0 ? 'text-blue-400' : 'text-red-400'}`}>
                  {b.current_net >= 0 ? '+' : ''}${b.current_net.toFixed(2)}
                </td>
                <td className="px-3 py-2 text-right text-gray-400 text-xs">
                  {b.bets_pending}p / {b.bets_won}w / {b.bets_lost}l
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr className="bg-gray-800 font-semibold border-t border-gray-600">
              <td className="px-3 py-2 text-gray-400 text-xs uppercase">Totals</td>
              <td className="px-3 py-2 text-right text-gray-200">${totals.net_bankroll.toFixed(2)}</td>
              <td className="px-3 py-2 text-right text-gray-300">${totals.net_wagered.toFixed(2)}</td>
              <td className="px-3 py-2 text-right text-gray-300">${totals.net_wagerable.toFixed(2)}</td>
              <td className={`px-3 py-2 text-right font-bold ${totals.net_total >= 0 ? 'text-blue-400' : 'text-red-400'}`}>
                {totals.net_total >= 0 ? '+' : ''}${totals.net_total.toFixed(2)}
              </td>
              <td />
            </tr>
          </tfoot>
        </table>
      </div>

      {/* Transfer Modal */}
      {transferOpen && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setTransferOpen(false)}>
          <div
            className="bg-gray-800 rounded-xl p-6 w-full max-w-sm shadow-2xl border border-gray-700"
            onClick={e => e.stopPropagation()}
          >
            <h2 className="text-lg font-semibold mb-4 text-gray-100">Transfer Funds</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-xs text-gray-400 mb-1">From</label>
                <select
                  value={form.sending}
                  onChange={e => setForm({ ...form, sending: e.target.value })}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm text-gray-100"
                >
                  {bookies.map(b => <option key={b.bookmaker} value={b.bookmaker}>{b.bookmaker}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">To</label>
                <select
                  value={form.receiving}
                  onChange={e => setForm({ ...form, receiving: e.target.value })}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm text-gray-100"
                >
                  {bookies.map(b => <option key={b.bookmaker} value={b.bookmaker}>{b.bookmaker}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">Amount ($)</label>
                <input
                  type="number"
                  step="any"
                  value={form.amount}
                  onChange={e => setForm({ ...form, amount: e.target.value })}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm text-gray-100"
                />
              </div>
            </div>
            <div className="mt-5 flex justify-between">
              <button
                onClick={transfer}
                disabled={submitting}
                className="px-4 py-2 rounded text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50"
              >
                {submitting ? 'Transferring…' : 'Transfer'}
              </button>
              <button onClick={() => setTransferOpen(false)} className="px-4 py-2 text-sm text-gray-400 hover:text-gray-200">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
