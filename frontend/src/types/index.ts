export interface Bet {
  bet_id: string;
  sport: string;
  team: string;
  bet_type: 'Moneyline' | 'Bonus';
  bookie: string;
  odds: number;
  bet_amount: number;
  bet_EV: number;
  this_EV: number;
  outcome: 'Pending' | 'win' | 'loss' | 'cancelled' | 'offset';
  net: number;
  date: string;
}

export interface EVBet {
  bet_id: string;
  sport: string;
  team: string;
  bookies: string[];
  odds: number;
  bet_EV: number;
  kelly_percent: number;
  date: string;
  kelly_wager: number;
}

export interface Bookie {
  bookmaker: string;
  deposit_total: number;
  withdrawal_total: number;
  total_bankroll: number;
  currently_wagered: number;
  wagerable: number;
  current_net: number;
  bets_placed: number;
  bets_settled: number;
  bets_won: number;
  bets_lost: number;
  bets_pending: number;
}

export interface BookieTotals {
  net_bankroll: number;
  net_wagered: number;
  net_wagerable: number;
  net_total: number;
}

export interface SettledTotals {
  total_ev: number;
  total_net: number;
  bets_won: number;
  bets_lost: number;
}

export interface GraphData {
  labels: string[];
  running_net: number[];
  running_ev: number[];
  constant_bet_net: number[];
  constant_bet_ev: number[];
  per_bookie: Record<string, number[]>;
  per_bookie_individual: Record<string, number[]>;
  per_bookie_individual_ev: Record<string, number[]>;
  bookies: string[];
  odds_categories: string[];
  odds_win_percentages: number[];
  odds_nets: number[];
}
