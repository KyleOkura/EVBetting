# EVBetting

A Flask + React app for tracking positive expected value (EV) sports bets.

## Stack

- **Backend**: Python / Flask — serves a JSON REST API under `/api/`
- **Database**: Turso (cloud libSQL), accessed via `libsql-experimental` (drop-in sqlite3 replacement)
- **Frontend**: Vite + React + TypeScript + Tailwind CSS

---

## Setup

### 1. Python environment

```bash
pip install -r requirements.txt
```

### 2. Environment variables

Copy `.env` and fill in your real values:

```
API_KEY = 'your-odds-api-key'
TURSO_URL = 'libsql://your-db-name.turso.io'
TURSO_AUTH_TOKEN = 'your-turso-auth-token'
```

Get your Turso credentials at [turso.tech](https://turso.tech). Create a database and run the schema setup once:

```bash
python -c "from tools.bet_history import create_tables; create_tables()"
```

### 3. Frontend dependencies

```bash
cd frontend
npm install
```

---

## Development

Run both servers simultaneously in two terminals:

### Terminal 1 — Flask API (port 5000)

```bash
cd website
flask run
```

### Terminal 2 — Vite dev server (port 5173)

```bash
cd frontend
npm run dev
```

The Vite dev server proxies all `/api/*` requests to Flask at `http://localhost:5000`, so CORS is handled transparently. Visit `http://localhost:5173` to use the app.

---

## Production Build

```bash
# Build the React app
cd frontend
npm run build

# Run Flask — it serves frontend/dist automatically
cd ../website
flask run
# Visit http://localhost:5000
```

Flask's catch-all route serves `frontend/dist/index.html` for all non-API paths.

---

## Project Structure

```
EVBetting/
├── website/
│   └── app.py               # Flask JSON API — all routes under /api/
├── frontend/
│   ├── src/
│   │   ├── types/index.ts   # TypeScript interfaces (Bet, EVBet, Bookie, …)
│   │   ├── components/
│   │   │   ├── Layout.tsx       # Sidebar navigation
│   │   │   ├── BetTable.tsx     # Reusable bet table with bookie filter
│   │   │   └── EditBetModal.tsx # Edit/settle bet modal
│   │   └── pages/
│   │       ├── Home.tsx         # Net profit per bookie
│   │       ├── SelectBets.tsx   # Available EV bets + Take Bet
│   │       ├── CurrentBets.tsx  # Pending bets
│   │       ├── AllBets.tsx      # All bets
│   │       ├── SettledBets.tsx  # Win/loss bets + stats
│   │       ├── BookieStats.tsx  # Bankroll table + Transfer Funds
│   │       └── Graphs.tsx       # Chart.js performance charts
│   └── public/              # Bookie logos (served as static assets)
├── tools/
│   ├── bet_history.py       # All DB operations (uses Turso via libsql-experimental)
│   ├── odds_calculator.py   # EV / Kelly criterion calculations
│   ├── run_sports.py        # Orchestrates bet detection from the-odds-api
│   └── get_sports.py        # Fetches active sports
├── requirements.txt
└── .env                     # API_KEY, TURSO_URL, TURSO_AUTH_TOKEN (never committed)
```

---

## API Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/home` | Bookie net profits |
| GET | `/api/select_bets` | Current EV bet opportunities |
| POST | `/api/refresh_bets` | Fetch fresh EV bets from the-odds-api |
| POST | `/api/take_bet` | Place a bet (moves from evbets → bets) |
| GET | `/api/current_bets` | Pending bets |
| GET | `/api/all_bets` | All bets |
| GET | `/api/settled_bets` | Win/loss bets + totals |
| POST | `/api/edit_bet` | Update odds, amount, date, bookie, outcome |
| GET | `/api/bookie_stats` | Per-bookie bankroll stats |
| POST | `/api/transfer_funds` | Transfer money between bookies |
| GET | `/api/graphs/data` | JSON data for Chart.js charts |
