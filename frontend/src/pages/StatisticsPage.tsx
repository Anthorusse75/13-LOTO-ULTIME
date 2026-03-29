import InfoTooltip from "@/components/common/InfoTooltip";
import PageIntro from "@/components/common/PageIntro";
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
        description="La page Statistiques analyse l'historique complet des tirages selon 7 angles différents. Ces analyses identifient des patterns dans les données pour guider la génération de grilles."
        tip="Les onglets Fréquences et Écarts sont les plus utiles pour un débutant. Les onglets Bayésien et Graphe offrent des analyses plus avancées."
        terms={[
          { term: "Fréquence", definition: "Nombre de fois qu'un numéro est apparu dans l'historique.", strength: "Facile à interpréter", limit: "Un numéro fréquent ne l'est pas forcément dans le futur" },
          { term: "Écart (retard)", definition: "Nombre de tirages écoulés depuis la dernière apparition d'un numéro.", strength: "Identifie les numéros 'en retard'", limit: "Chaque tirage est indépendant : le retard ne crée pas d'obligation" },
          { term: "Cooccurrence", definition: "Paires de numéros qui apparaissent souvent dans le même tirage.", strength: "Utile pour construire des combinaisons cohérentes" },
          { term: "Tendance temporelle", definition: "Analyse de l'évolution des fréquences sur des fenêtres de temps récentes.", strength: "Détecte les numéros en montée ou en descente", limit: "Significatif seulement si R² > 0.5" },
          { term: "Bayésien", definition: "Éstimation probabiliste enrichie par les données historiques. Retourne la probabilité que chaque numéro sorte.", strength: "Plus robuste que la simple fréquence" },
          { term: "Graphe", definition: "Représentation réseau des co-occurrences. Les numéros centraux sont ceux qui 'jouent bien ensemble' avec beaucoup d'autres." },
        ]}
      />

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
      {renderTab()}
    </div>
  );
}
