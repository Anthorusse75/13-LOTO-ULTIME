import NotificationBell from "@/components/notifications/NotificationBell";
import { useAuthStore } from "@/stores/authStore";
import { useSettingsStore } from "@/stores/settingsStore";
import {
  BarChart3,
  BookOpen,
  Briefcase,
  Dices,
  FlaskConical,
  Heart,
  HelpCircle,
  History,
  Layers,
  LayoutDashboard,
  LogOut,
  Menu,
  Moon,
  Scale,
  Settings,
  Sun,
  Target,
  Wallet,
  X,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";

type NavItem = {
  to: string;
  icon: typeof LayoutDashboard;
  label: string;
  adminOnly?: boolean;
};

type NavCategory = { title: string; items: NavItem[] };

const navCategories: NavCategory[] = [
  {
    title: "Analyse",
    items: [
      { to: "/", icon: LayoutDashboard, label: "Dashboard" },
      { to: "/draws", icon: Dices, label: "Tirages" },
      { to: "/statistics", icon: BarChart3, label: "Statistiques" },
    ],
  },
  {
    title: "Génération",
    items: [
      { to: "/grids", icon: Target, label: "Grilles" },
      { to: "/portfolio", icon: Briefcase, label: "Portefeuille" },
      { to: "/wheeling", icon: Layers, label: "Système réduit" },
      { to: "/budget", icon: Wallet, label: "Budget" },
    ],
  },
  {
    title: "Évaluation",
    items: [
      { to: "/simulation", icon: FlaskConical, label: "Simulation" },
      { to: "/comparator", icon: Scale, label: "Comparateur" },
      { to: "/favorites", icon: Heart, label: "Favoris" },
    ],
  },
  {
    title: "Outils",
    items: [
      { to: "/history", icon: History, label: "Historique" },
      { to: "/how-it-works", icon: HelpCircle, label: "Comment ça marche" },
      { to: "/glossary", icon: BookOpen, label: "Glossaire" },
    ],
  },
  {
    title: "Admin",
    items: [
      {
        to: "/admin",
        icon: Settings,
        label: "Administration",
        adminOnly: true,
      },
    ],
  },
];

export default function Sidebar() {
  const collapsed = useSettingsStore((s) => s.sidebarCollapsed);
  const toggleSidebar = useSettingsStore((s) => s.toggleSidebar);
  const logout = useAuthStore((s) => s.logout);
  const user = useAuthStore((s) => s.user);
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Close mobile drawer on route change
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMobileOpen(false);
  }, [location.pathname]);

  // Close on Escape key
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === "Escape") setMobileOpen(false);
  }, []);

  useEffect(() => {
    if (mobileOpen) {
      document.addEventListener("keydown", handleKeyDown);
      return () => document.removeEventListener("keydown", handleKeyDown);
    }
  }, [mobileOpen, handleKeyDown]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const theme = useSettingsStore((s) => s.theme);
  const toggleTheme = useSettingsStore((s) => s.toggleTheme);

  const filteredCategories = navCategories
    .map((cat) => ({
      ...cat,
      items: cat.items.filter(
        (item) => !item.adminOnly || user?.role === "ADMIN",
      ),
    }))
    .filter((cat) => cat.items.length > 0);

  const navContent = (mobile: boolean) => (
    <>
      <nav
        className="flex-1 py-2 overflow-y-auto"
        role="navigation"
        aria-label="Menu principal"
      >
        {filteredCategories.map((cat) => (
          <div key={cat.title} className="mb-1">
            {(mobile || !collapsed) && (
              <p className="px-4 pt-3 pb-1 text-[10px] font-bold uppercase tracking-widest text-text-secondary/60">
                {cat.title}
              </p>
            )}
            {collapsed && !mobile && (
              <div className="mx-auto my-1 w-6 border-t border-border" />
            )}
            {cat.items.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-2 mx-2 rounded-md text-sm transition-colors ${
                    isActive
                      ? "bg-accent-blue/10 text-accent-blue border-l-2 border-accent-blue"
                      : "text-text-secondary hover:bg-surface-hover hover:text-text-primary"
                  }`
                }
                aria-current={location.pathname === to ? "page" : undefined}
              >
                <Icon size={18} aria-hidden="true" />
                {(mobile || !collapsed) && <span>{label}</span>}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="p-4 border-t border-border space-y-2">
        <button
          onClick={toggleTheme}
          className="flex items-center gap-2 w-full px-2 py-1.5 rounded-md text-sm text-text-secondary hover:bg-surface-hover transition-colors"
          aria-label={
            theme === "dark" ? "Passer en mode clair" : "Passer en mode sombre"
          }
        >
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          {(mobile || !collapsed) && (
            <span>{theme === "dark" ? "Mode clair" : "Mode sombre"}</span>
          )}
        </button>
        {(mobile || !collapsed) && user && (
          <p
            className="text-xs text-text-secondary truncate"
            title={user.email}
          >
            {user.username} ({user.role})
          </p>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 w-full px-2 py-1.5 rounded-md text-sm text-text-secondary hover:bg-surface-hover hover:text-accent-red transition-colors"
          aria-label="Se déconnecter"
        >
          <LogOut size={18} aria-hidden="true" />
          {(mobile || !collapsed) && <span>Déconnexion</span>}
        </button>
        {(mobile || !collapsed) && (
          <p className="text-xs text-text-secondary text-center">v1.0.0</p>
        )}
      </div>
    </>
  );

  return (
    <>
      {/* Mobile hamburger button */}
      <button
        onClick={() => setMobileOpen(true)}
        className="fixed top-3 left-3 z-40 p-2 rounded-md bg-surface border border-border text-text-secondary hover:bg-surface-hover md:hidden"
        aria-label="Ouvrir le menu"
      >
        <Menu size={20} />
      </button>

      {/* Mobile drawer overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-50 md:hidden"
          role="dialog"
          aria-modal="true"
          aria-label="Menu de navigation"
        >
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="relative flex flex-col w-64 h-full bg-surface border-r border-border">
            <div className="flex items-center justify-between h-14 px-4 border-b border-border">
              <span className="font-bold text-accent-blue text-lg tracking-tight">
                LOTO ULTIME
              </span>
              <div className="ml-auto mr-2">
                <NotificationBell />
              </div>
              <button
                onClick={() => setMobileOpen(false)}
                className="p-1.5 rounded-md hover:bg-surface-hover text-text-secondary"
                aria-label="Fermer le menu"
              >
                <X size={20} />
              </button>
            </div>
            {navContent(true)}
          </aside>
        </div>
      )}

      {/* Desktop sidebar */}
      <aside
        className={`hidden md:flex flex-col bg-surface border-r border-border transition-all duration-200 ${
          collapsed ? "w-16" : "w-60"
        }`}
        role="navigation"
        aria-label="Menu principal"
      >
        <div className="flex items-center h-14 px-4 border-b border-border">
          <button
            onClick={toggleSidebar}
            className="p-1.5 rounded-md hover:bg-surface-hover text-text-secondary"
            aria-label={collapsed ? "Déplier le menu" : "Replier le menu"}
          >
            <Menu size={20} />
          </button>
          {!collapsed && (
            <span className="ml-3 font-bold text-accent-blue text-lg tracking-tight">
              LOTO ULTIME
            </span>
          )}
          <div className="ml-auto">
            <NotificationBell />
          </div>
        </div>
        {navContent(false)}
      </aside>
    </>
  );
}
