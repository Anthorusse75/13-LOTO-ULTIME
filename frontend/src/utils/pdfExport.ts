/**
 * PDF export utilities using jsPDF.
 * Supports exporting a single grid and a full analysis report.
 */
import type { GridScoreResponse } from "@/types/grid";
import jsPDF from "jspdf";

const ACCENT_BLUE = [59, 130, 246] as const; // Tailwind blue-500
const ACCENT_GREEN = [34, 197, 94] as const; // Tailwind green-500
const ACCENT_PURPLE = [168, 85, 247] as const; // Tailwind purple-500
const GRAY_700 = [55, 65, 81] as const;
const GRAY_400 = [156, 163, 175] as const;

function addHeader(doc: jsPDF, title: string) {
  doc.setFillColor(17, 24, 39); // gray-900
  doc.rect(0, 0, 210, 18, "F");
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(12);
  doc.setFont("helvetica", "bold");
  doc.text("LOTO ULTIME", 10, 12);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.text(title, 60, 12);
  doc.setTextColor(...GRAY_400);
  doc.setFontSize(8);
  doc.text(new Date().toLocaleDateString("fr-FR"), 175, 12);
}

function addBall(
  doc: jsPDF,
  x: number,
  y: number,
  num: number,
  color: readonly [number, number, number],
) {
  doc.setFillColor(...color);
  doc.circle(x, y, 5, "F");
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(8);
  doc.setFont("helvetica", "bold");
  const text = String(num);
  const w = doc.getTextWidth(text);
  doc.text(text, x - w / 2, y + 2.5);
}

function drawNumbers(
  doc: jsPDF,
  numbers: number[],
  stars: number[] | null | undefined,
  y: number,
) {
  let x = 15;
  for (const n of numbers) {
    addBall(doc, x, y, n, ACCENT_BLUE);
    x += 14;
  }
  if (stars && stars.length > 0) {
    x += 5;
    for (const s of stars) {
      addBall(doc, x, y, s, ACCENT_PURPLE);
      x += 14;
    }
  }
}

function drawScoreBar(
  doc: jsPDF,
  label: string,
  value: number,
  y: number,
  barWidth = 80,
) {
  doc.setTextColor(...GRAY_700);
  doc.setFontSize(8);
  doc.setFont("helvetica", "normal");
  doc.text(label, 15, y);

  // Background bar
  doc.setFillColor(229, 231, 235);
  doc.roundedRect(60, y - 4, barWidth, 5, 1, 1, "F");

  // Filled bar
  const filled = Math.max(0, Math.min(1, value)) * barWidth;
  const r =
    value >= 0.7
      ? ACCENT_GREEN
      : value >= 0.4
        ? ([234, 179, 8] as const)
        : ([239, 68, 68] as const);
  doc.setFillColor(r[0], r[1], r[2]);
  if (filled > 0) doc.roundedRect(60, y - 4, filled, 5, 1, 1, "F");

  doc.setTextColor(...GRAY_400);
  doc.text(`${(value * 10).toFixed(1)}`, 145, y);
}

export function exportGridPDF(
  grid: GridScoreResponse,
  gameName = "Jeu",
  method = "auto",
) {
  const doc = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });

  addHeader(doc, `Grille — ${gameName}`);

  // Title section
  doc.setTextColor(...GRAY_700);
  doc.setFontSize(14);
  doc.setFont("helvetica", "bold");
  doc.text("Grille optimisée", 15, 30);

  doc.setFontSize(9);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(...GRAY_400);
  doc.text(`Méthode : ${method}`, 15, 37);
  doc.text(`Score global : ${(grid.total_score * 10).toFixed(2)} / 10`, 15, 43);

  // Draw the numbers
  doc.setTextColor(...GRAY_700);
  doc.setFontSize(9);
  doc.setFont("helvetica", "bold");
  doc.text("Numéros :", 15, 55);
  drawNumbers(doc, grid.numbers, grid.stars, 63);

  // Score breakdown
  doc.setFontSize(11);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(...GRAY_700);
  doc.text("Détail des scores", 15, 80);

  const criteria = [
    { key: "frequency", label: "Fréquences" },
    { key: "gap", label: "Écarts" },
    { key: "cooccurrence", label: "Cooccurrences" },
    { key: "structure", label: "Structure" },
    { key: "balance", label: "Balance" },
    { key: "pattern_penalty", label: "Pénalité motifs" },
  ];

  let y = 90;
  for (const c of criteria) {
    const val =
      grid.score_breakdown[c.key as keyof typeof grid.score_breakdown] ?? 0;
    drawScoreBar(doc, c.label, val, y);
    y += 10;
  }

  // Footer
  doc.setFillColor(243, 244, 246);
  doc.rect(0, 278, 210, 19, "F");
  doc.setFontSize(7);
  doc.setTextColor(...GRAY_400);
  doc.text(
    "Généré par Loto Ultime — outil d'aide statistique uniquement. Aucune garantie de gain.",
    15,
    285,
  );
  doc.text(
    "Le jeu excessif peut être dangereux. Jouez avec modération.",
    15,
    290,
  );

  doc.save(`grille-${grid.numbers.join("-")}.pdf`);
}

interface ReportData {
  gameName: string;
  grids: GridScoreResponse[];
  method: string;
  computationMs: number;
}

export function exportReportPDF({
  gameName,
  grids,
  method,
  computationMs,
}: ReportData) {
  const doc = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });

  addHeader(doc, `Rapport d'analyse — ${gameName}`);

  doc.setTextColor(...GRAY_700);
  doc.setFontSize(14);
  doc.setFont("helvetica", "bold");
  doc.text("Rapport d'analyse de grilles", 15, 30);

  doc.setFontSize(9);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(...GRAY_400);
  doc.text(
    `Méthode : ${method}  ·  Grilles analysées : ${grids.length}  ·  Temps : ${computationMs.toFixed(0)} ms`,
    15,
    38,
  );
  doc.text(
    `Date : ${new Date().toLocaleDateString("fr-FR")} ${new Date().toLocaleTimeString("fr-FR")}`,
    15,
    44,
  );

  // Summary statistics
  const scores = grids.map((g) => g.total_score);
  const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
  const max = Math.max(...scores);

  doc.setFontSize(11);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(...GRAY_700);
  doc.text("Résumé", 15, 55);

  doc.setFontSize(9);
  doc.setFont("helvetica", "normal");
  doc.text(`Score moyen : ${(avg * 10).toFixed(2)} / 10`, 15, 63);
  doc.text(`Meilleur score : ${(max * 10).toFixed(2)} / 10`, 80, 63);

  // Grilles table header
  doc.setFontSize(10);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(...GRAY_700);
  doc.text("Grilles générées", 15, 75);

  doc.setFillColor(243, 244, 246);
  doc.rect(10, 78, 190, 7, "F");
  doc.setFontSize(8);
  doc.setTextColor(...GRAY_700);
  doc.text("#", 13, 83);
  doc.text("Numéros", 25, 83);
  doc.text("Score", 165, 83);
  doc.text("Méthode", 180, 83);

  let y = 92;
  for (let i = 0; i < grids.length && y < 270; i++) {
    const g = grids[i];
    if (i % 2 === 0) {
      doc.setFillColor(249, 250, 251);
      doc.rect(10, y - 5, 190, 7, "F");
    }
    doc.setFontSize(8);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(...GRAY_700);
    doc.text(String(i + 1), 13, y);
    const nums = [
      ...g.numbers.map(String),
      ...(g.stars ? g.stars.map((s) => `★${s}`) : []),
    ].join("  ");
    doc.text(nums, 25, y);
    doc.setTextColor(...ACCENT_GREEN);
    doc.text(`${(g.total_score * 10).toFixed(1)}`, 166, y);
    doc.setTextColor(...GRAY_400);
    doc.text(method, 181, y);
    y += 8;

    if (y > 270) {
      doc.addPage();
      addHeader(doc, `Rapport d'analyse — ${gameName} (suite)`);
      y = 30;
    }
  }

  // Footer
  doc.setPage(doc.getNumberOfPages());
  doc.setFillColor(243, 244, 246);
  doc.rect(0, 278, 210, 19, "F");
  doc.setFontSize(7);
  doc.setTextColor(...GRAY_400);
  doc.text(
    "Généré par Loto Ultime — outil d'aide statistique uniquement. Aucune garantie de gain.",
    15,
    285,
  );
  doc.text(
    "Le jeu excessif peut être dangereux. Jouez avec modération.",
    15,
    290,
  );

  doc.save(`rapport-analyse-${new Date().toISOString().slice(0, 10)}.pdf`);
}
