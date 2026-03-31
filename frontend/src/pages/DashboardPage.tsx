import Disclaimer from "@/components/common/Disclaimer";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import PageIntro from "@/components/common/PageIntro";
import StatOfTheDay from "@/components/dashboard/StatOfTheDay";
import type { StatHighlight } from "@/components/dashboard/StatOfTheDay";
import DrawBalls from "@/components/draws/DrawBalls";
import { useDraws, useLatestDraw } from "@/hooks/useDraws";
import { useTopGrids } from "@/hooks/useGrids";
import { useSchedulerStatus } from "@/hooks/useJobs";
import { useStatistics } from "@/hooks/useStatistics";
import { useAuthStore } from "@/stores/authStore";
import { formatDate, formatScore } from "@/utils/formatters";
import {
  Activity,
  Award,
  Calendar,
  Flame,
  Hash,
  Hourglass,
  Percent,
  Snowflake,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function DashboardPage() {
  const isAdmin = useAuthStore((s) => s.user?.role === "ADMIN");
  const {
    data: stats,
    isLoading: statsLoading,
    isError: statsError,
  } = useStatistics();
  const { data: latest } = useLatestDraw();
  const { data: drawsResponse } = useDraws(1, 5);
  const { data: topGrids } = useTopGrids(5);
  const { data: schedulerStatus } = useSchedulerStatus(isAdmin);

  if (statsLoading)
    return <LoadingSpinner message="Chargement du dashboard..." />;

  const draws = drawsResponse?.items;
  const noData = statsError && !draws?.length;

  const topFreq = stats?.frequencies
    .slice()
    .sort((a, b) => b.relative - a.relative)
    .slice(0, 10);

  // Derive stat highlights
  const mostOverdue = stats?.gaps
    ?.slice()
    .sort((a, b) => b.current_gap - a.current_gap)[0];

  const leastFreq = stats?.frequencies
    ?.slice()
    .sort((a, b) => a.relative - b.relative)[0];

  const statHighlights: StatHighlight[] = [];
  if (topFreq?.[0]) {
    statHighlights.push({
      icon: <Flame size={16} className="text-accent-red" />,
      label: "le plus fréquent",
      value: `N°${topFreq[0].number}`,
      detail: `${(topFreq[0].relative * 100).toFixed(1)}% des tirages (${topFreq[0].count} apparitions)`,
      color: "text-accent-red",
    });
  }
  if (mostOverdue) {
    statHighlights.push({
      icon: <Hourglass size={16} className="text-accent-amber" />,
      label: "le plus en retard",
      value: `N°${mostOverdue.number}`,
      detail: `Absent depuis ${mostOverdue.current_gap} tirages (max historique : ${mostOverdue.max_gap})`,
      color: "text-accent-amber",
    });
  }
  if (leastFreq) {
    statHighlights.push({
      icon: <Snowflake size={16} className="text-accent-blue" />,
      label: "le plus rare",
      value: `N°${leastFreq.number}`,
      detail: `${(leastFreq.relative * 100).toFixed(1)}% des tirages seulement`,
      color: "text-accent-blue",
    });
  }
  if (stats) {
    statHighlights.push({
      icon: <Percent size={16} className="text-accent-green" />,
      label: "uniformité",
      value: `${(stats.uniformity_score * 100).toFixed(0)}%`,
      detail: `Entropie ${stats.distribution_entropy.toFixed(2)} — ${stats.uniformity_score > 0.9 ? "distribution très uniforme" : stats.uniformity_score > 0.7 ? "distribution équilibrée" : "distribution déséquilibrée"}`,
      color: "text-accent-green",
    });
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      {noData && (
        <div className="bg-accent-blue/10 border border-accent-blue/30 rounded-lg p-4 text-sm">
          <p className="font-semibold mb-1">Aucune donnée disponible</p>
          <p className="text-text-secondary">
            Le pipeline d'import se lance automatiquement au premier démarrage.
            Les tirages et statistiques apparaîtront d'ici quelques minutes.
            Vous pouvez aussi déclencher l'import manuellement depuis la page
            Administration.
          </p>
        </div>
      )}

      <PageIntro
        storageKey="dashboard"
        description="Bienvenue ! Le Dashboard est votre tableau de bord principal. Il résume en un coup d'œil tout ce qui se passe : les derniers tirages officiels récupérés, vos meilleures grilles calculées par nos algorithmes, et l'état du système automatique qui met tout à jour chaque nuit."
        tip="Si c'est votre première visite, tout se met en place automatiquement — les tirages sont importés et les statistiques calculées en arrière-plan. Revenez dans quelques minutes si certaines données n'apparaissent pas encore. Ensuite, explorez les pages Statistiques et Grilles pour découvrir les analyses."
        terms={[
          {
            term: "Tirage",
            definition:
              "Résultat officiel de la loterie : les numéros gagnants tirés à une date donnée. Par exemple, pour le Loto du 29 mars : 5 - 12 - 23 - 34 - 45 + N°Chance 7.",
          },
          {
            term: "Score d'une grille",
            definition:
              "Note de 0 à 10 calculée par nos algorithmes à partir de 6 critères statistiques (fréquence, écart, cooccurrence, structure, équilibre, originalité). Ce n'est pas une prédiction — c'est une mesure de qualité statistique.",
            strength:
              "Permet de comparer objectivement des grilles entre elles",
            limit:
              "La loterie reste un jeu de hasard — un bon score n'augmente pas vos chances de gagner",
          },
          {
            term: "Hot numbers (numéros chauds)",
            definition:
              "Les numéros qui sont sortis le plus souvent dans l'historique récent. Par exemple, si le 7 est sorti 8 fois sur les 50 derniers tirages, il est « chaud ».",
          },
          {
            term: "Cold numbers (numéros froids)",
            definition:
              "Les numéros qui sortent rarement ou qui ne sont pas sortis depuis longtemps. Certains joueurs pensent qu'ils sont « dus » et vont bientôt sortir.",
          },
          {
            term: "Pipeline nocturne",
            definition:
              "Chaque nuit à 22h, le système récupère automatiquement les nouveaux tirages, recalcule toutes les statistiques et régénère les meilleures grilles. Tout est automatique.",
            strength: "Vous avez toujours des données à jour sans rien faire",
          },
        ]}
      />

      {/* KPI cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Dernier tirage"
          icon={<Hash size={18} />}
          value={
            latest ? (
              <DrawBalls
                numbers={latest.numbers}
                stars={latest.stars}
                size="sm"
              />
            ) : (
              "—"
            )
          }
          sub={latest ? formatDate(latest.draw_date) : ""}
        />
        <KpiCard
          title="Tirages analysés"
          icon={<Award size={18} />}
          value={stats?.draw_count ?? "—"}
          sub="dans la base"
        />
        <KpiCard
          title="Hot numbers"
          icon={<TrendingUp size={18} className="text-accent-green" />}
          value={stats?.hot_numbers?.slice(0, 5).join(", ") ?? "—"}
          sub="fréquences élevées"
        />
        <KpiCard
          title="Cold numbers"
          icon={<TrendingDown size={18} className="text-accent-red" />}
          value={stats?.cold_numbers?.slice(0, 5).join(", ") ?? "—"}
          sub="fréquences basses"
        />
      </div>

      {/* Pipeline health */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <KpiCard
          title="Pipeline nocturne"
          icon={
            <Activity
              size={18}
              className={
                schedulerStatus ? "text-accent-green" : "text-accent-red"
              }
            />
          }
          value={schedulerStatus ? "Actif" : "Inactif"}
          sub={`${schedulerStatus?.running_count ?? 0} jobs en cours`}
        />
        <KpiCard
          title="Meilleure grille"
          icon={<Calendar size={18} />}
          value={topGrids?.[0] ? formatScore(topGrids[0].total_score) : "—"}
          sub={
            topGrids?.[0]
              ? `méthode ${topGrids[0].method}`
              : "aucune grille générée"
          }
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Stat of the day */}
        <StatOfTheDay items={statHighlights} />

        {/* Frequency chart */}
        <div className="bg-surface rounded-lg border border-border p-4">
          <h2 className="text-sm font-semibold mb-4">Top 10 Fréquences</h2>
          {topFreq && topFreq.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={topFreq}>
                  <XAxis
                    dataKey="number"
                    tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
                  />
                  <YAxis
                    tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "var(--color-surface)",
                      border: "1px solid var(--color-border)",
                      borderRadius: 6,
                    }}
                    labelStyle={{ color: "var(--color-text-primary)" }}
                  />
                  <Bar
                    dataKey="relative"
                    fill="var(--color-accent-blue)"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
              <p className="text-xs text-text-secondary mt-2">
                Les 10 numéros les plus fréquemment tirés. Plus la barre est
                haute, plus le numéro sort souvent. La hauteur représente la
                fréquence relative (proportionnelle au nombre de tirages).
              </p>
            </>
          ) : (
            <p className="text-text-secondary text-sm">Aucune donnée</p>
          )}
        </div>

        {/* Top grids */}
        <div className="bg-surface rounded-lg border border-border p-4">
          <h2 className="text-sm font-semibold mb-4">Top 5 Grilles</h2>
          {topGrids && topGrids.length > 0 ? (
            <div className="space-y-3">
              {topGrids.map((g, i) => (
                <div
                  key={g.id}
                  className="flex items-center gap-3 p-2 rounded-md hover:bg-surface-hover"
                >
                  <span className="text-xs text-text-secondary w-5">
                    #{i + 1}
                  </span>
                  <DrawBalls numbers={g.numbers} stars={g.stars} size="sm" />
                  <span className="ml-auto font-mono text-accent-green text-sm">
                    {formatScore(g.total_score)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-text-secondary text-sm">Aucune grille générée</p>
          )}
        </div>
      </div>

      {/* Recent draws */}
      <div className="bg-surface rounded-lg border border-border p-4">
        <h2 className="text-sm font-semibold mb-4">Derniers tirages</h2>
        {draws && draws.length > 0 ? (
          <div className="space-y-2">
            {draws.map((d) => (
              <div
                key={d.id}
                className="flex items-center gap-4 p-2 rounded-md hover:bg-surface-hover"
              >
                <span className="text-xs text-text-secondary w-20">
                  {formatDate(d.draw_date)}
                </span>
                {d.draw_number && (
                  <span className="text-xs text-text-secondary w-12">
                    #{d.draw_number}
                  </span>
                )}
                <DrawBalls numbers={d.numbers} stars={d.stars} size="sm" />
              </div>
            ))}
          </div>
        ) : (
          <p className="text-text-secondary text-sm">Aucun tirage</p>
        )}
      </div>

      <Disclaimer />
    </div>
  );
}

function KpiCard({
  title,
  icon,
  value,
  sub,
}: {
  title: string;
  icon: React.ReactNode;
  value: React.ReactNode;
  sub: string;
}) {
  return (
    <div className="bg-surface rounded-lg border border-border p-4">
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <span className="text-xs text-text-secondary">{title}</span>
      </div>
      <div className="text-lg font-semibold">{value}</div>
      <p className="text-xs text-text-secondary mt-1">{sub}</p>
    </div>
  );
}
