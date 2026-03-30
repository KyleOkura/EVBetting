import { NavLink, Outlet } from 'react-router-dom';

const navItems = [
  { to: '/', label: 'Home', end: true },
  { to: '/select-bets', label: 'Available Bets' },
  { to: '/current-bets', label: 'Pending Bets' },
  { to: '/all-bets', label: 'All Bets' },
  { to: '/settled-bets', label: 'Settled Bets' },
  { to: '/bookie-stats', label: 'Bookie Stats' },
  { to: '/graphs', label: 'Graphs' },
];

export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex">
      {/* Sidebar */}
      <aside className="w-52 shrink-0 bg-gray-950 border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <img src="/evbetlogo.png" alt="EVBet" className="w-16 h-16 mx-auto" />
          <p className="text-center text-xs text-gray-400 mt-1 font-semibold tracking-widest uppercase">EVBetting</p>
        </div>
        <nav className="flex-1 py-4">
          {navItems.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `block px-4 py-2.5 text-sm transition-colors ${
                  isActive
                    ? 'bg-indigo-600 text-white font-medium'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-gray-100'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-6 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
