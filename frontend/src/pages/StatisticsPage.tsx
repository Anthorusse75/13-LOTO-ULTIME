import InfoTooltip from "@/components/common/InfoTooltip";
import PageIntro from "@/components/common/PageIntro";
import BayesianTab from "@/components/statistics/BayesianTab";
import CooccurrenceTab from "@/components/statistics/CooccurrenceTab";
import DistributionTab from "@/components/statistics/DistributionTab";
import FrequencyTab from "@/components/statistics/FrequencyTab";
import GapTab from "@/components/statistics/GapTab";
import GraphTab from "@/components/statistics/GraphTab";
import StarsTab from "@/components/statistics/StarsTab";
import TemporalTab from "@/components/statistics/TemporalTab";
import { useStatistics } from "@/hooks/useStatistics";
import { gameService } from "@/services/gameService";
import { useGameStore } from "@/stores/gameStore";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

const BASE_TABS = [
  {
    key: "frequencies",
    label: "Fréquences",
    tooltip: "Nombre de fois où chaque numéro a été tiré.",
  },
  {
    key: "gaps",
    label: "Écarts",
    tooltip:
      "Nombre de tirages depuis la dernière apparition de chaque numéro.",
  },
  {
    key: "cooccurrences",
    label: "Cooccurrences",
    tooltip: "Paires de numéros qui apparaissent souvent ensemble.",
  },
  {
    key: "temporal",
    label: "Tendances",
    tooltip: "Évolution des fréquences sur différentes fenêtres temporelles.",
  },
  {
    key: "distribution",
    label: "Distribution",
    tooltip: "Analyse de l'uniformité et de la répartition des tirages.",
  },
  {
    key: "bayesian",
    label: "Bayésien",
    tooltip:
      "Estimation bayésienne des probabilités d'apparition (modèle Beta-Binomial).",
  },
  {
    key: "graph",
    label: "Graphe",
    tooltip: "Réseau de co-occurrence : communautés et centralité des numéros.",
  },
] as const;

type BaseTabKey = (typeof BASE_TABS)[number]["key"];
type TabKey = BaseTabKey | "stars";

const PERIOD_OPTIONS = [
  { value: undefined, label: "Tous les tirages" },
  { value: 50, label: "50 derniers" },
  { value: 100, label: "100 derniers" },
  { value: 200, label: "200 derniers" },
] as const;

type PeriodValue = (typeof PERIOD_OPTIONS)[number]["value"];

const PERIOD_SUPPORTED_TABS: TabKey[] = ["frequencies", "gaps"];

export default function StatisticsPage() {
  const [activeTab, setActiveTab] = useState<TabKey>("frequencies");
  const [lastN, setLastN] = useState<PeriodValue>(undefined);

  const slug = useGameStore((s) => s.currentGameSlug);
  const { data: game } = useQuery({
    queryKey: ["game", slug],
    queryFn: () => gameService.getBySlug(slug!),
    enabled: !!slug,
  });
  const { data: stats } = useStatistics();

  const hasStars = !!(
    stats?.star_frequencies && stats.star_frequencies.length > 0
  );
  const starTabLabel = game?.star_name
    ? game.star_name.charAt(0).toUpperCase() + game.star_name.slice(1) + "s"
    : "Étoiles";

  const tabs = useMemo(() => {
    const base = BASE_TABS as unknown as Array<{
      key: TabKey;
      label: string;
      tooltip: string;
    }>;
    if (!hasStars) return base;
    return [
      ...base,
      {
        key: "stars" as TabKey,
        label: starTabLabel,
        tooltip: `Fréquences et écarts des ${starTabLabel.toLowerCase()} (numéros complémentaires).`,
      },
    ];
  }, [hasStars, starTabLabel]);

  const showPeriodSelector = PERIOD_SUPPORTED_TABS.includes(activeTab);

  function renderTab() {
    switch (activeTab) {
      case "frequencies":
        return <FrequencyTab lastN={lastN} />;
      case "gaps":
        return <GapTab lastN={lastN} />;
      case "cooccurrences":
        return <CooccurrenceTab />;
      case "temporal":
        return <TemporalTab />;
      case "distribution":
        return <DistributionTab />;
      case "bayesian":
        return <BayesianTab />;
      case "graph":
        return <GraphTab />;
      case "stars":
        return <StarsTab />;
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="text-2xl font-bold">Statistiques</h1>
        {showPeriodSelector && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-text-secondary">Période :</span>
            <div className="flex gap-1">
              {PERIOD_OPTIONS.map((opt) => (
                <button
                  key={String(opt.value)}
                  onClick={() => setLastN(opt.value)}
                  className={`px-2.5 py-1 rounded text-xs transition-colors ${
                    lastN === opt.value
                      ? "bg-accent-blue text-white"
                      : "bg-surface-hover text-text-secondary hover:text-text-primary border border-border"
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <PageIntro
        storageKey="statistics"
        description="La page Statistiques analyse l'historique complet des tirages selon 7 angles différents. Chaque onglet apporte un éclairage différent pour comprendre le comportement des numéros. Ces analyses alimentent ensuite le score de vos grilles — c'est le cerveau du système."
        tip="Si vous débutez, commencez par l'onglet Fréquences (quels numéros sortent le plus ?) puis Écarts (lesquels sont en retard ?). Les onglets Bayésien et Graphe utilisent des mathématiques plus avancées mais leurs résultats sont résumés simplement. Le sélecteur « Période » en haut à droite permet de ne regarder que les 50 ou 100 derniers tirages — utile pour repérer les tendances récentes."
        terms={[
          {
            term: "Fréquence",
            definition:
              "Combien de fois un numéro est sorti dans l'historique. Exemple : si le 7 est sorti 85 fois sur 1000 tirages, sa fréquence est de 8.5%. La moyenne théorique pour le Loto (5 numéros parmi 49) est d'environ 10.2% par numéro.",
            strength: "Facile à comprendre — un bon point de départ",
            limit:
              "Un numéro « chaud » peut refroidir du jour au lendemain — chaque tirage est indépendant",
          },
          {
            term: "Écart (retard)",
            definition:
              "Le nombre de tirages qui se sont passés depuis la dernière fois qu'un numéro est sorti. Exemple : si le 23 n'est sorti à aucun des 40 derniers tirages, son écart est de 40. Si en moyenne il sort tous les 10 tirages, il est « en retard ».",
            strength:
              "Permet de repérer les numéros qui sont absents depuis longtemps",
            limit:
              "Attention au « biais du joueur » : le retard ne crée aucune obligation de sortie — la loterie n'a pas de mémoire",
          },
          {
            term: "Cooccurrence",
            definition:
              "Les paires de numéros qui sortent souvent ensemble dans le même tirage. Exemple : si le 7 et le 12 sont sortis ensemble 15 fois alors que la moyenne est de 5, c'est une paire forte. Utile pour construire des grilles avec des associations « historiquement gagnantes ».",
            strength:
              "Aide à construire des grilles cohérentes (numéros qui « vont ensemble »)",
          },
          {
            term: "Tendance temporelle",
            definition:
              "Analyse comment la fréquence d'un numéro évolue dans le temps récent. Un numéro peut être peu fréquent globalement mais en forte hausse sur les 50 derniers tirages — c'est la tendance qui le détecte.",
            strength: "Détecte les numéros « en montée » ou « en descente »",
            limit:
              "Fiable surtout quand la tendance est nette (indicateur R² > 0.5)",
          },
          {
            term: "Distribution",
            definition:
              "Vérifie si les tirages passés sont répartis uniformément ou s'il y a des déséquilibres. Par exemple, est-ce que les numéros 1-10 sortent autant que les 40-49 ? L'entropie de Shannon mesure cette uniformité.",
          },
          {
            term: "Bayésien",
            definition:
              "Estimation « intelligente » de la probabilité de chaque numéro, qui combine la théorie (chaque numéro a la même chance) avec les données réelles. Plus robuste que la simple fréquence car elle ne « sur-réagit » pas aux anomalies récentes.",
            strength:
              "Plus fiable que la fréquence brute, surtout avec peu de données",
          },
          {
            term: "Graphe",
            definition:
              "Réseau visuel où chaque numéro est un point, et les liens représentent les co-occurrences. Les numéros au centre du réseau (forte centralité) sont ceux qui « jouent bien » avec le plus d'autres numéros.",
          },
        ]}
      />

      {/* Tab bar */}
      <div className="flex gap-1 overflow-x-auto border-b border-border pb-px">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 text-sm rounded-t-md transition-colors whitespace-nowrap ${
              activeTab === tab.key
                ? "bg-surface text-accent-blue border-b-2 border-accent-blue"
                : "text-text-secondary hover:text-text-primary hover:bg-surface-hover"
            }`}
          >
            {tab.label}
            <InfoTooltip text={tab.tooltip} />
          </button>
        ))}
      </div>

      {/* Tab content */}
      {renderTab()}
    </div>
  );
}
