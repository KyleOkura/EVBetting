import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import SelectBets from './pages/SelectBets';
import CurrentBets from './pages/CurrentBets';
import AllBets from './pages/AllBets';
import SettledBets from './pages/SettledBets';
import BookieStats from './pages/BookieStats';
import Graphs from './pages/Graphs';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="select-bets" element={<SelectBets />} />
          <Route path="current-bets" element={<CurrentBets />} />
          <Route path="all-bets" element={<AllBets />} />
          <Route path="settled-bets" element={<SettledBets />} />
          <Route path="bookie-stats" element={<BookieStats />} />
          <Route path="graphs" element={<Graphs />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
