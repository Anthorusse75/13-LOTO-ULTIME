export function formatNumber(n: number, decimals = 2): string {
  return n.toFixed(decimals);
}

export function formatPercent(n: number, decimals = 1): string {
  return `${(n * 100).toFixed(decimals)}%`;
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("fr-FR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}

export function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString("fr-FR");
}

export function formatScore(score: number): string {
  return (score * 10).toFixed(2);
}
