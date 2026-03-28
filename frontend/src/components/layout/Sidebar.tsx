import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Dices,
  BarChart3,
  Target,
  Briefcase,
  FlaskConical,
  Settings,
  Menu,
} from "lucide-react";
import { useSettingsStore } from "@/stores/settingsStore";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/draws", icon: Dices, label: "Tirages" },
  { to: "/statistics", icon: BarChart3, label: "Statistiques" },
  { to: "/grids", icon: Target, label: "Grilles" },
  { to: "/portfolio", icon: Briefcase, label: "Portefeuille" },
  { to: "/simulation", icon: FlaskConical, label: "Simulation" },
  { to: "/admin", icon: Settings, label: "Admin" },
];

export default function Sidebar() {
  const collapsed = useSettingsStore((s) => s.sidebarCollapsed);
  const toggleSidebar = useSettingsStore((s) => s.toggleSidebar);

  return (
    <aside
      className={`flex flex-col bg-surface border-r border-border transition-all duration-200 ${
        collapsed ? "w-16" : "w-60"
      }`}
    >
      <div className="flex items-center h-14 px-4 border-b border-border">
        <button
          onClick={toggleSidebar}
          className="p-1.5 rounded-md hover:bg-surface-hover text-text-secondary"
          aria-label="Toggle sidebar"
        >
          <Menu size={20} />
        </button>
        {!collapsed && (
          <span className="ml-3 font-bold text-accent-blue text-lg tracking-tight">
            LOTO ULTIME
          </span>
        )}
      </div>

      <nav className="flex-1 py-2">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 mx-2 rounded-md text-sm transition-colors ${
                isActive
                  ? "bg-accent-blue/10 text-accent-blue border-l-2 border-accent-blue"
                  : "text-text-secondary hover:bg-surface-hover hover:text-text-primary"
              }`
            }
          >
            <Icon size={20} />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-border text-xs text-text-secondary text-center">
        {!collapsed && "v1.0.0"}
      </div>
    </aside>
  );
}
