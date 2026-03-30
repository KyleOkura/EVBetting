import { useState } from 'react';
import type { Bet } from '../types';
import EditBetModal from './EditBetModal';

const BOOKIES = [
  'all', 'draftkings', 'fanduel', 'betmgm', 'betrivers',
  'ballybet', 'espnbet', 'fanatics', 'williamhill_us', 'cash',
];

function outcomeClass(outcome: string) {
  switch (outcome) {
    case 'win': return 'text-blue-400';
    case 'loss': return 'text-red-400';
    case 'cancelled': return 'text-yellow-400';
    default: return 'text-gray-400';
  }
}

function fmtNet(net: number) {
  const sign = net >= 0 ? '+' : '';
  return `${sign}$${net.toFixed(2)}`;
}

interface Props {
  bets: Bet[];
  showNet?: boolean;
  totalEV?: number;
  totalWagered?: number;
  totalNet?: number;
  betsWon?: number;
  betsLost?: number;
  onRefresh: () => void;
}

export default function BetTable({
  bets,
  showNet = false,
  totalEV,
  totalWagered,
  totalNet,
  betsWon,
  betsLost,
  onRefresh,
}: Props) {
  const [filterBookie, setFilterBookie] = useState('all');
  const [editingBet, setEditingBet] = useState<Bet | null>(null);

  const filtered = filterBookie === 'all'
    ? bets
    : bets.filter(b => b.bookie === filterBookie);

  return (
    <>
      {editingBet && (
        <EditBetModal
          bet={editingBet}
          onClose={() => setEditingBet(null)}
          onSaved={onRefresh}
        />
      )}

      <div className="mb-3 flex items-center gap-3">
        <label className="text-sm text-gray-400">Filter:</label>
        <select
          value={filterBookie}
          onChange={e => setFilterBookie(e.target.value)}
          className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm text-gray-100 focus:outline-none"
        >
          {BOOKIES.map(b => <option key={b} value={b}>{b === 'all' ? 'All Bookies' : b}</option>)}
        </select>
      </div>

      <div className="overflow-x-auto rounded-lg border border-gray-700">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-800 text-gray-400 text-xs uppercase tracking-wider">
              <th className="px-3 py-2 text-left">Date</th>
              <th className="px-3 py-2 text-left">Team</th>
              <th className="px-3 py-2 text-left">Sport</th>
              <th className="px-3 py-2 text-left">Bookie</th>
              <th className="px-3 py-2 text-right">Odds</th>
              <th className="px-3 py-2 text-left">Type</th>
              <th className="px-3 py-2 text-right">Amount</th>
              <th className="px-3 py-2 text-right">EV</th>
              {showNet && <th className="px-3 py-2 text-right">Net</th>}
              <th className="px-3 py-2 text-left">Outcome</th>
              <th className="px-3 py-2"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {filtered.map(bet => (
              <tr key={bet.bet_id} className="hover:bg-gray-800/50 transition-colors">
                <td className="px-3 py-2 text-gray-300 whitespace-nowrap">{bet.date}</td>
                <td className="px-3 py-2 text-gray-100 font-medium max-w-[180px] truncate">{bet.team}</td>
                <td className="px-3 py-2 text-gray-400">{bet.sport}</td>
                <td className="px-3 py-2 text-gray-300">{bet.bookie}</td>
                <td className="px-3 py-2 text-right text-gray-200">
                  {bet.odds > 0 ? `+${bet.odds}` : bet.odds}
                </td>
                <td className="px-3 py-2 text-gray-400">{bet.bet_type}</td>
                <td className="px-3 py-2 text-right text-gray-200">${bet.bet_amount}</td>
                <td className="px-3 py-2 text-right text-emerald-400">${bet.this_EV?.toFixed(2)}</td>
                {showNet && (
                  <td className={`px-3 py-2 text-right font-medium ${bet.net >= 0 ? 'text-blue-400' : 'text-red-400'}`}>
                    {fmtNet(bet.net)}
                  </td>
                )}
                <td className={`px-3 py-2 font-medium ${outcomeClass(bet.outcome)}`}>{bet.outcome}</td>
                <td className="px-3 py-2">
                  <button
                    onClick={() => setEditingBet(bet)}
                    className="text-xs px-2 py-1 rounded bg-gray-700 hover:bg-gray-600 text-gray-300"
                  >
                    Edit
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
          {/* Totals row */}
          <tfoot>
            <tr className="bg-gray-800 font-medium text-gray-300 border-t border-gray-600">
              <td colSpan={7} className="px-3 py-2 text-gray-400 text-xs uppercase">Totals</td>
              <td className="px-3 py-2 text-right text-emerald-400">
                {totalEV !== undefined && `$${totalEV.toFixed(2)}`}
              </td>
              {showNet && (
                <td className={`px-3 py-2 text-right font-semibold ${(totalNet ?? 0) >= 0 ? 'text-blue-400' : 'text-red-400'}`}>
                  {totalNet !== undefined && fmtNet(totalNet)}
                </td>
              )}
              <td className="px-3 py-2 text-xs text-gray-400">
                {betsWon !== undefined && `W: ${betsWon} / L: ${betsLost}`}
              </td>
              <td />
            </tr>
            {totalWagered !== undefined && (
              <tr className="bg-gray-800 text-gray-400 text-xs">
                <td colSpan={11} className="px-3 py-1">
                  Total wagered: <span className="text-gray-200">${totalWagered.toFixed(2)}</span>
                </td>
              </tr>
            )}
          </tfoot>
        </table>
      </div>
    </>
  );
}
