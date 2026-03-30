import { useState } from 'react';
import axios from 'axios';
import type { Bet } from '../types';

const BOOKIES = [
  'draftkings', 'fanduel', 'betmgm', 'betrivers',
  'ballybet', 'espnbet', 'fanatics', 'williamhill_us', 'cash',
];

interface Props {
  bet: Bet;
  onClose: () => void;
  onSaved: () => void;
}

export default function EditBetModal({ bet, onClose, onSaved }: Props) {
  const [odds, setOdds] = useState('');
  const [date, setDate] = useState(bet.date);
  const [amount, setAmount] = useState('');
  const [bookie, setBookie] = useState(bet.bookie);
  const [betType, setBetType] = useState(bet.bet_type);
  const [saving, setSaving] = useState(false);

  async function submit(outcome?: string) {
    setSaving(true);
    await axios.post('/api/edit_bet', {
      bet_id: bet.bet_id,
      odds: odds || undefined,
      date,
      amount: amount || undefined,
      bookie,
      bet_type: betType,
      outcome,
    });
    setSaving(false);
    onSaved();
    onClose();
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-gray-800 rounded-xl p-6 w-full max-w-md shadow-2xl border border-gray-700"
        onClick={e => e.stopPropagation()}
      >
        <h2 className="text-lg font-semibold mb-4 text-gray-100">Edit Bet</h2>

        <div className="space-y-3">
          <div>
            <label className="block text-xs text-gray-400 mb-1">Team</label>
            <p className="text-sm text-gray-200">{bet.team} — {bet.sport}</p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Odds</label>
              <input
                type="number"
                placeholder={String(bet.odds)}
                value={odds}
                onChange={e => setOdds(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm text-gray-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Amount ($)</label>
              <input
                type="number"
                step="any"
                placeholder={String(bet.bet_amount)}
                value={amount}
                onChange={e => setAmount(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm text-gray-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs text-gray-400 mb-1">Date</label>
            <input
              type="date"
              value={date}
              onChange={e => setDate(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm text-gray-100 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Bookie</label>
              <select
                value={bookie}
                onChange={e => setBookie(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm text-gray-100 focus:outline-none focus:border-indigo-500"
              >
                {BOOKIES.map(b => <option key={b} value={b}>{b}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Bet Type</label>
              <select
                value={betType}
                onChange={e => setBetType(e.target.value as 'Moneyline' | 'Bonus')}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm text-gray-100 focus:outline-none focus:border-indigo-500"
              >
                <option value="Moneyline">Moneyline</option>
                <option value="Bonus">Bonus</option>
              </select>
            </div>
          </div>
        </div>

        {/* Outcome buttons */}
        <div className="mt-4">
          <label className="block text-xs text-gray-400 mb-2">Set Outcome</label>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => submit('win')}
              disabled={saving}
              className="px-3 py-1.5 rounded text-sm font-medium bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50"
            >Win</button>
            <button
              onClick={() => submit('loss')}
              disabled={saving}
              className="px-3 py-1.5 rounded text-sm font-medium bg-red-700 hover:bg-red-600 text-white disabled:opacity-50"
            >Loss</button>
            <button
              onClick={() => submit('Pending')}
              disabled={saving}
              className="px-3 py-1.5 rounded text-sm font-medium bg-gray-600 hover:bg-gray-500 text-white disabled:opacity-50"
            >Pending</button>
            <button
              onClick={() => submit('cancelled')}
              disabled={saving}
              className="px-3 py-1.5 rounded text-sm font-medium bg-yellow-600 hover:bg-yellow-500 text-white disabled:opacity-50"
            >Cancelled</button>
          </div>
        </div>

        <div className="mt-5 flex justify-between">
          <button
            onClick={() => submit()}
            disabled={saving}
            className="px-4 py-2 rounded text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50"
          >
            {saving ? 'Saving…' : 'Save Changes'}
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded text-sm text-gray-400 hover:text-gray-200"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
