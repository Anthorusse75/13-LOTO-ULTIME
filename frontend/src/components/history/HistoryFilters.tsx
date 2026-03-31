const TYPE_OPTIONS: { value: string; label: string }[] = [
  { value: "", label: "Tous les types" },
  { value: "grid", label: "Grilles" },
  { value: "portfolio", label: "Portfolios" },
  { value: "simulation", label: "Simulations" },
  { value: "comparison", label: "Comparaisons" },
  { value: "wheeling", label: "Wheeling" },
  { value: "budget_plan", label: "Plans budget" },
];

interface HistoryFiltersProps {
  resultType: string;
  onResultTypeChange: (v: string) => void;
  favoritesOnly: boolean;
  onFavoritesOnlyChange: (v: boolean) => void;
}

export default function HistoryFilters({
  resultType,
  onResultTypeChange,
  favoritesOnly,
  onFavoritesOnlyChange,
}: HistoryFiltersProps) {
  return (
    <div className="flex items-center gap-3 flex-wrap">
      <select
        value={resultType}
        onChange={(e) => onResultTypeChange(e.target.value)}
        className="bg-surface-hover border border-border rounded-md px-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-accent-blue"
      >
        {TYPE_OPTIONS.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>

      <label className="flex items-center gap-1.5 text-xs text-text-secondary cursor-pointer">
        <input
          type="checkbox"
          checked={favoritesOnly}
          onChange={(e) => onFavoritesOnlyChange(e.target.checked)}
          className="rounded border-border"
        />
        Favoris uniquement
      </label>
    </div>
  );
}
