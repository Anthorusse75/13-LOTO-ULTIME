import { useState } from "react";
import FrequencyTab from "@/components/statistics/FrequencyTab";
import GapTab from "@/components/statistics/GapTab";
import CooccurrenceTab from "@/components/statistics/CooccurrenceTab";
import TemporalTab from "@/components/statistics/TemporalTab";
import DistributionTab from "@/components/statistics/DistributionTab";
import BayesianTab from "@/components/statistics/BayesianTab";
import GraphTab from "@/components/statistics/GraphTab";

const TABS = [
  { key: "frequencies", label: "Fréquences" },
  { key: "gaps", label: "Écarts" },
  { key: "cooccurrences", label: "Cooccurrences" },
  { key: "temporal", label: "Tendances" },
  { key: "distribution", label: "Distribution" },
  { key: "bayesian", label: "Bayésien" },
  { key: "graph", label: "Graphe" },
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
          </button>
        ))}
      </div>

      {/* Tab content */}
      <ActiveComponent />
    </div>
  );
}
