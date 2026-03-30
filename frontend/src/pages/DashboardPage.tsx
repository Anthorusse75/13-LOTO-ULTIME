import Disclaimer from "@/components/common/Disclaimer";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import PageIntro from "@/components/common/PageIntro";
import DrawBalls from "@/components/draws/DrawBalls";
import { useDraws, useLatestDraw } from "@/hooks/useDraws";
import { useTopGrids } from "@/hooks/useGrids";
import { useSchedulerStatus } from "@/hooks/useJobs";
import { useStatistics } from "@/hooks/useStatistics";
import { formatDate, formatScore } from "@/utils/formatters";
import {
  Activity,
  Award,
  Calendar,
  Hash,
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
  const { data: stats, isLoading: statsLoading, isError: statsError } = useStatistics();
  const { data: latest } = useLatestDraw();
  const { data: draws } = useDraws(0, 5);
  const { data: topGrids } = useTopGrids(5);
  const { data: schedulerStatus } = useSchedulerStatus();

  if (statsLoading)
    return <LoadingSpinner message="Chargement du dashboard..." />;

  const noData = statsError && !draws?.length;

  const topFreq = stats?.frequencies
    .slice()
    .sort((a, b) => b.relative - a.relative)
    .slice(0, 10);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      {noData && (
        <div className="bg-accent-blue/10 border border-accent-blue/30 rounded-lg p-4 text-sm">
          <p className="font-semibold mb-1">Aucune donnée disponible</p>
          <p className="text-text-secondary">
            Le pipeline d'import se lance automatiquement au premier démarrage.
            Les tirages et statistiques apparaîtront d'ici quelques minutes.
            Vous pouvez aussi déclencher l'import manuellement depuis la page Administration.
          </p>
        </div>
      )}

      <PageIntro
        storageKey="dashboard"
        description="Le Dashboard est votre point d'entrée. Il résume en un coup d'œil l'état de votre activité : les derniers tirages officiels, vos meilleures grilles calculées et la santé du pipeline de calcul automatique."
        tip="Commencez par importer des tirages depuis la page Administration, puis lancez le calcul des statistiques pour alimenter toutes les analyses."
        terms={[
          {
            term: "Tirage",
            definition:
              "Résultat officiel de la loterie : les numéros gagnants d'une date donnée.",
          },
          {
            term: "Score d'une grille",
            definition:
              "Note de 0 à 10 calculée par nos algorithmes. Plus il est élevé, plus la grille est statistiquement intéressante.",
            strength: "Permet de comparer objectivement des grilles",
            limit: "Ne prédit pas le résultat — la loterie reste aléatoire",
          },
          {
            term: "Pipeline",
            definition:
              "Enchaînement automatique des étapes : import des tirages → calcul des statistiques → génération de grilles.",
            strength: "Se relance chaque nuit à 22h automatiquement",
          },
          {
            term: "Fréquence",
            definition:
              "Nombre de fois qu'un numéro est apparu dans l'historique des tirages.",
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
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
                Fréquences relatives des 10 numéros les plus tirés.
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
