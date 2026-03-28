import InfoTooltip from "@/components/common/InfoTooltip";
import BayesianTab from "@/components/statistics/BayesianTab";
import CooccurrenceTab from "@/components/statistics/CooccurrenceTab";
import DistributionTab from "@/components/statistics/DistributionTab";
import FrequencyTab from "@/components/statistics/FrequencyTab";
import GapTab from "@/components/statistics/GapTab";
import GraphTab from "@/components/statistics/GraphTab";
import TemporalTab from "@/components/statistics/TemporalTab";
import { useState } from "react";

const TABS = [
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

type TabKey = (typeof TABS)[number]["key"];

const TAB_COMPONENTS: Record<TabKey, React.FC> = {
  frequencies: FrequencyTab,
  gaps: GapTab,
  cooccurrences: CooccurrenceTab,
  temporal: TemporalTab,
  distribution: DistributionTab,
  bayesian: BayesianTab,
  graph: GraphTab,
};

export default function StatisticsPage() {
  const [activeTab, setActiveTab] = useState<TabKey>("frequencies");
  const ActiveComponent = TAB_COMPONENTS[activeTab];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Statistiques</h1>

      {/* Tab bar */}
      <div className="flex gap-1 overflow-x-auto border-b border-border pb-px">
        {TABS.map((tab) => (
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
      <ActiveComponent />
    </div>
  );
}
