import { NavLink, Outlet } from "react-router-dom";
import "./Layout.css";

const Icon = ({ name }) => {
  const paths = {
    scan: <><path d="M4 8V5a1 1 0 0 1 1-1h3M16 4h3a1 1 0 0 1 1 1v3M20 16v3a1 1 0 0 1-1 1h-3M8 20H5a1 1 0 0 1-1-1v-3"/><path d="M8 12h8"/></>,
    history: <><circle cx="12" cy="12" r="8"/><path d="M12 7v5l3 2"/></>,
    analytics: <><path d="M5 20v-6M10 20V9M15 20V4M20 20v-9"/></>,
    admin: <><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.83 2.83-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 .6 1.7 1.7 0 0 0-.4 1v.1h-4V21a1.7 1.7 0 0 0-1.1-1.6 1.7 1.7 0 0 0-1.88.34l-.06.06-2.83-2.83.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-.6-1 1.7 1.7 0 0 0-1-.4h-.1v-4H3A1.7 1.7 0 0 0 4.6 8.5a1.7 1.7 0 0 0-.34-1.88l-.06-.06 2.83-2.83.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-.6 1.7 1.7 0 0 0 .4-1v-.1h4V3A1.7 1.7 0 0 0 15.5 4.6a1.7 1.7 0 0 0 1.88-.34l.06-.06 2.83 2.83-.06.06A1.7 1.7 0 0 0 19.4 9c.39.27.68.62.6 1v4c.08.38-.21.73-.6 1Z"/></>,
  };
  return <svg className="sidebar__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
};

const NAV_ITEMS = [
  { to: "/scan", label: "Scan", icon: "scan" },
  { to: "/history", label: "History", icon: "history" },
  { to: "/analytics", label: "Analytics", icon: "analytics" },
  { to: "/admin", label: "Admin", icon: "admin" },
];

export default function Layout() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar__brand">
          <h1 className="sidebar__name">LMPC Scanner</h1>
          <p className="sidebar__tagline">SCAN · VERIFY · STAY SAFE</p>
          <span className="sidebar__rule" />
          <p className="sidebar__eyebrow">SIH26034</p>
        </div>
        <nav className="sidebar__nav" aria-label="Primary navigation">
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => `sidebar__link${isActive ? " sidebar__link--active" : ""}`}>
              <Icon name={item.icon} /><span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar__footnote"><span className="sidebar__rule" />Safer Choices<br />Brighter Tomorrows</div>
      </aside>
      <main className="content"><Outlet /></main>
    </div>
  );
}
