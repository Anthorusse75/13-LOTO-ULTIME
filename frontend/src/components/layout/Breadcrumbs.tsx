import { ChevronRight, Home } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

const ROUTE_LABELS: Record<string, string> = {
  draws: "Tirages",
  statistics: "Statistiques",
  grids: "Grilles",
  portfolio: "Portefeuille",
  simulation: "Simulation",
  wheeling: "Système réduit",
  budget: "Budget",
  comparator: "Comparateur",
  history: "Historique",
  favorites: "Favoris",
  "how-it-works": "Comment ça marche",
  glossary: "Glossaire",
  admin: "Administration",
  login: "Connexion",
};

export default function Breadcrumbs() {
  const location = useLocation();
  const segments = location.pathname.split("/").filter(Boolean);

  if (segments.length === 0) return null;

  return (
    <nav
      aria-label="Fil d'Ariane"
      className="flex items-center gap-1 text-xs text-text-secondary mb-4"
    >
      <Link
        to="/"
        className="flex items-center gap-1 hover:text-text-primary transition-colors"
      >
        <Home size={12} />
        <span>Accueil</span>
      </Link>
      {segments.map((seg, i) => {
        const path = "/" + segments.slice(0, i + 1).join("/");
        const label = ROUTE_LABELS[seg] || seg;
        const isLast = i === segments.length - 1;

        return (
          <span key={path} className="flex items-center gap-1">
            <ChevronRight size={12} className="text-text-secondary/50" />
            {isLast ? (
              <span className="text-text-primary font-medium">{label}</span>
            ) : (
              <Link
                to={path}
                className="hover:text-text-primary transition-colors"
              >
                {label}
              </Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}
