import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Moon, Sun, ChevronDown } from "lucide-react";
import { useSettingsStore } from "@/stores/settingsStore";
import { useGameStore } from "@/stores/gameStore";
import { gameService } from "@/services/gameService";
import type { GameDefinition } from "@/types/game";

export default function Header() {
  const theme = useSettingsStore((s) => s.theme);
  const toggleTheme = useSettingsStore((s) => s.toggleTheme);
  const currentGameId = useGameStore((s) => s.currentGameId);
  const setGame = useGameStore((s) => s.setGame);

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

  const currentGame = games?.find((g) => g.id === currentGameId);

  return (
    <header className="flex items-center justify-between h-14 px-6 bg-surface border-b border-border">
      <div className="flex items-center gap-4">
        <h1 className="text-sm font-medium text-text-secondary">
          {currentGame ? currentGame.name : "Chargement..."}
        </h1>
      </div>

      <div className="flex items-center gap-3">
        {/* Game selector */}
        {games && games.length > 1 && (
          <div className="relative">
            <select
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
            />
          </div>
        )}

        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-md hover:bg-surface-hover text-text-secondary"
          aria-label="Toggle theme"
        >
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  );
}
