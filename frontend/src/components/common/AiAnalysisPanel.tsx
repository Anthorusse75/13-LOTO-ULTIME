import { useAiAnalysis } from "@/hooks/useCoach";
import { Loader2, RefreshCw, Sparkles } from "lucide-react";
import { useCallback, useEffect, useRef } from "react";

interface AiAnalysisPanelProps {
  /** The analysis topic sent to the backend (grid, statistics, portfolio, simulation, dashboard). */
  topic: string;
  /** A function that builds the context data to send. Called on each analysis request. */
  buildContext: () => Record<string, unknown>;
  /** A stable key that changes when the underlying data changes (triggers reset). */
  dataKey: string;
  /** Button label. Default: "Demander une analyse IA" */
  buttonLabel?: string;
  /** Description shown before analysis. */
  description?: string;
}

export default function AiAnalysisPanel({
  topic,
  buildContext,
  dataKey,
  buttonLabel = "Demander une analyse IA experte",
  description,
}: AiAnalysisPanelProps) {
  const mutation = useAiAnalysis();
  const lastKeyRef = useRef<string>("");

  const ask = useCallback(() => {
    if (mutation.isPending) return;
    mutation.mutate({ topic, context: buildContext() });
  }, [topic, buildContext, mutation]);

  // Reset when underlying data changes
  useEffect(() => {
    if (lastKeyRef.current !== dataKey) {
      lastKeyRef.current = dataKey;
      mutation.reset();
    }
  }, [dataKey]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="bg-accent-purple/5 border border-accent-purple/20 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-accent-purple" />
          <span className="text-sm font-semibold text-accent-purple">
            Analyse IA
          </span>
        </div>
        {mutation.data?.advice && (
          <button
            onClick={ask}
            disabled={mutation.isPending}
            className="text-accent-purple hover:text-accent-purple/80 transition-colors"
            title="Relancer l'analyse"
          >
            <RefreshCw
              className={`w-4 h-4 ${mutation.isPending ? "animate-spin" : ""}`}
            />
          </button>
        )}
      </div>

      {mutation.data?.advice ? (
        <p className="text-sm text-text-primary leading-relaxed">
          {mutation.data.advice}
        </p>
      ) : mutation.isPending ? (
        <div className="flex items-center gap-2 py-3">
          <Loader2 className="w-4 h-4 animate-spin text-accent-purple" />
          <span className="text-sm text-text-secondary">
            L'expert analyse vos données…
          </span>
        </div>
      ) : (
        <>
          {description && (
            <p className="text-xs text-text-secondary mb-3">{description}</p>
          )}
          <button
            onClick={ask}
            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg bg-accent-purple/10 hover:bg-accent-purple/20 transition-colors text-sm font-medium text-accent-purple"
          >
            <Sparkles className="w-4 h-4" />
            {buttonLabel}
          </button>
        </>
      )}
    </div>
  );
}
