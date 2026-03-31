import { gameService } from "@/services/gameService";
import { useGameStore } from "@/stores/gameStore";
import { useSettingsStore } from "@/stores/settingsStore";
import type { GameDefinition } from "@/types/game";
import { useQuery } from "@tanstack/react-query";
import {
  BookOpen,
  ChevronDown,
  HelpCircle,
  Info,
  Moon,
  Sun,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Header() {
  const theme = useSettingsStore((s) => s.theme);
  const toggleTheme = useSettingsStore((s) => s.toggleTheme);
  const currentGameId = useGameStore((s) => s.currentGameId);
  const setGame = useGameStore((s) => s.setGame);
  const [infoOpen, setInfoOpen] = useState(false);
  const infoRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const { data: games } = useQuery<GameDefinition[]>({
    queryKey: ["games"],
    queryFn: gameService.getAll,
    staleTime: 10 * 60 * 1000,
  });

  // Auto-select first game if none selected
  useEffect(() => {
    if (!currentGameId && games && games.length > 0) {
      setGame(games[0].id, games[0].slug);
    }
  }, [currentGameId, games, setGame]);

  // Close dropdown on click outside
  useEffect(() => {
    if (!infoOpen) return;
    const handleClick = (e: MouseEvent) => {
      if (infoRef.current && !infoRef.current.contains(e.target as Node)) {
        setInfoOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [infoOpen]);

  const currentGame = games?.find((g) => g.id === currentGameId);

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-14 px-6 bg-surface border-b border-border">
      <div className="flex items-center gap-4">
        <h1 className="text-sm font-medium text-text-secondary">
          {currentGame ? currentGame.name : "Chargement..."}
        </h1>
      </div>

      <div className="flex items-center gap-3">
        {/* Game selector */}
        {games && games.length > 1 && (
          <div className="relative">
            <label htmlFor="game-selector" className="sr-only">
              Choisir un jeu
            </label>
            <select
              id="game-selector"
              value={currentGameId ?? ""}
              onChange={(e) => {
                const g = games.find((g) => g.id === Number(e.target.value));
                if (g) setGame(g.id, g.slug);
              }}
              className="appearance-none bg-surface-hover border border-border rounded-md px-3 py-1.5 pr-8 text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-accent-blue"
            >
              {games.map((g) => (
                <option key={g.id} value={g.id}>
                  {g.name}
                </option>
              ))}
            </select>
            <ChevronDown
              size={14}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-text-secondary pointer-events-none"
              aria-hidden="true"
            />
          </div>
        )}

        {/* Info dropdown */}
        <div className="relative" ref={infoRef}>
          <button
            onClick={() => setInfoOpen(!infoOpen)}
            className="p-2 rounded-md hover:bg-surface-hover text-text-secondary"
            aria-label="Informations et aide"
            aria-expanded={infoOpen}
          >
            <Info size={18} aria-hidden="true" />
          </button>
          {infoOpen && (
            <div className="absolute right-0 top-full mt-1 w-56 bg-surface border border-border rounded-lg shadow-lg py-1 z-50">
              <button
                onClick={() => {
                  navigate("/how-it-works");
                  setInfoOpen(false);
                }}
                className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-text-secondary hover:bg-surface-hover hover:text-text-primary transition-colors text-left"
              >
                <HelpCircle size={16} />
                Comment ça marche
              </button>
              <button
                onClick={() => {
                  navigate("/glossary");
                  setInfoOpen(false);
                }}
                className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-text-secondary hover:bg-surface-hover hover:text-text-primary transition-colors text-left"
              >
                <BookOpen size={16} />
                Glossaire
              </button>
            </div>
          )}
        </div>

        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-md hover:bg-surface-hover text-text-secondary"
          aria-label={
            theme === "dark" ? "Passer en mode clair" : "Passer en mode sombre"
          }
        >
          {theme === "dark" ? (
            <Sun size={18} aria-hidden="true" />
          ) : (
            <Moon size={18} aria-hidden="true" />
          )}
        </button>
      </div>
    </header>
  );
}
