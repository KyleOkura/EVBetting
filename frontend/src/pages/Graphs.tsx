import { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import type { GraphData } from '../types';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

const LINE_OPTS = {
  responsive: true,
  animation: false as const,
  plugins: { legend: { labels: { color: '#9ca3af' } } },
  scales: {
    x: { ticks: { color: '#6b7280', maxTicksLimit: 12 }, grid: { color: '#1f2937' } },
    y: { ticks: { color: '#9ca3af' }, grid: { color: '#1f2937' } },
  },
};

const BAR_OPTS = {
  responsive: true,
  animation: false as const,
  plugins: { legend: { labels: { color: '#9ca3af' } } },
  scales: {
    x: { ticks: { color: '#9ca3af' }, grid: { color: '#1f2937' } },
    y: { ticks: { color: '#9ca3af' }, grid: { color: '#1f2937' } },
  },
};

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 p-4">
      <h2 className="text-sm font-semibold text-gray-300 mb-3 uppercase tracking-wide">{title}</h2>
      {children}
    </div>
  );
}

const BOOKIE_COLORS = [
  '#60a5fa', '#f87171', '#34d399', '#fbbf24',
  '#a78bfa', '#fb923c', '#38bdf8', '#f472b6', '#4ade80',
];

export default function Graphs() {
  const [data, setData] = useState<GraphData | null>(null);

  useEffect(() => {
    axios.get<GraphData>('/api/graphs/data').then(r => setData(r.data));
  }, []);

  if (!data) return <p className="text-gray-400 text-sm">Loading charts…</p>;

  const { labels, running_net, running_ev, constant_bet_net, constant_bet_ev,
    per_bookie, per_bookie_individual, per_bookie_individual_ev,
    bookies, odds_categories, odds_win_percentages, odds_nets } = data;

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-100 mb-5">Performance Graphs</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Running net vs EV */}
        <ChartCard title="Running Net vs Running EV">
          <Line
            options={LINE_OPTS}
            data={{
              labels,
              datasets: [
                { label: 'Net', data: running_net, borderColor: '#60a5fa', backgroundColor: 'transparent', pointRadius: 0, tension: 0.1 },
                { label: 'EV', data: running_ev, borderColor: '#34d399', backgroundColor: 'transparent', pointRadius: 0, tension: 0.1, borderDash: [4, 4] },
              ],
            }}
          />
        </ChartCard>

        {/* Constant $5 bet */}
        <ChartCard title="Constant $5 Bet Net vs EV">
          <Line
            options={LINE_OPTS}
            data={{
              labels,
              datasets: [
                { label: 'Net ($5)', data: constant_bet_net, borderColor: '#f87171', backgroundColor: 'transparent', pointRadius: 0, tension: 0.1 },
                { label: 'EV ($5)', data: constant_bet_ev, borderColor: '#fbbf24', backgroundColor: 'transparent', pointRadius: 0, tension: 0.1, borderDash: [4, 4] },
              ],
            }}
          />
        </ChartCard>

        {/* Odds category net */}
        <ChartCard title="Net by Odds Category">
          <Bar
            options={BAR_OPTS}
            data={{
              labels: odds_categories,
              datasets: [
                {
                  label: 'Net',
                  data: odds_nets,
                  backgroundColor: odds_nets.map(v => v >= 0 ? 'rgba(96,165,250,0.7)' : 'rgba(248,113,113,0.7)'),
                },
              ],
            }}
          />
        </ChartCard>

        {/* Odds category win % */}
        <ChartCard title="Win % by Odds Category">
          <Bar
            options={{
              ...BAR_OPTS,
              scales: {
                ...BAR_OPTS.scales,
                y: { ...BAR_OPTS.scales.y, min: 0, max: 1, ticks: { color: '#9ca3af', callback: (v: number | string) => `${Math.round(Number(v) * 100)}%` } },
              },
            }}
            data={{
              labels: odds_categories,
              datasets: [
                {
                  label: 'Win %',
                  data: odds_win_percentages,
                  backgroundColor: 'rgba(52,211,153,0.7)',
                },
              ],
            }}
          />
        </ChartCard>

        {/* Per-bookie combined */}
        <ChartCard title="Per-Bookie Cumulative Net">
          <Line
            options={LINE_OPTS}
            data={{
              labels,
              datasets: bookies.map((b, i) => ({
                label: b,
                data: per_bookie[b] ?? [],
                borderColor: BOOKIE_COLORS[i % BOOKIE_COLORS.length],
                backgroundColor: 'transparent',
                pointRadius: 0,
                tension: 0.1,
              })),
            }}
          />
        </ChartCard>

        {/* Individual bookie charts */}
        {bookies.map((b, i) => {
          const netData = per_bookie_individual[b];
          const evData = per_bookie_individual_ev[b];
          if (!netData || netData.length === 0) return null;
          const betLabels = netData.map((_, idx) => String(idx + 1));
          return (
            <ChartCard key={b} title={b}>
              <Line
                options={LINE_OPTS}
                data={{
                  labels: betLabels,
                  datasets: [
                    { label: 'Net', data: netData, borderColor: BOOKIE_COLORS[i % BOOKIE_COLORS.length], backgroundColor: 'transparent', pointRadius: 0, tension: 0.1 },
                    { label: 'EV', data: evData, borderColor: BOOKIE_COLORS[(i + 4) % BOOKIE_COLORS.length], backgroundColor: 'transparent', pointRadius: 0, tension: 0.1, borderDash: [4, 4] },
                  ],
                }}
              />
            </ChartCard>
          );
        })}
      </div>
    </div>
  );
}
