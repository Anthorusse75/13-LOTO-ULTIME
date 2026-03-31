import type { Explanation } from "@/types/explanation";
import {
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  Lightbulb,
  Sparkles,
} from "lucide-react";
import { useState } from "react";

interface ExplanationPanelProps {
  explanation: Explanation;
  defaultExpanded?: boolean;
}

export default function ExplanationPanel({
  explanation,
  defaultExpanded = false,
}: ExplanationPanelProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  return (
    <div className="bg-surface rounded-lg border border-border overflow-hidden">
      {/* Summary — always visible */}
      <button
        onClick={() => setExpanded((e) => !e)}
        className="w-full flex items-center gap-2 px-4 py-3 text-left hover:bg-surface-hover transition-colors"
        aria-expanded={expanded}
      >
        <Sparkles size={16} className="text-accent-blue shrink-0" />
        <span className="text-sm font-medium flex-1">
          {explanation.summary}
        </span>
        {expanded ? (
          <ChevronDown size={14} className="text-text-secondary shrink-0" />
        ) : (
          <ChevronRight size={14} className="text-text-secondary shrink-0" />
        )}
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-3 border-t border-border pt-3">
          {/* Interpretation (L2) */}
          <p className="text-sm text-text-secondary leading-relaxed">
            {explanation.interpretation}
          </p>

          {/* Highlights */}
          {explanation.highlights.length > 0 && (
            <div className="space-y-1">
              {explanation.highlights.map((h, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2 text-xs text-accent-green"
                >
                  <Lightbulb size={12} className="mt-0.5 shrink-0" />
                  <span>{h}</span>
                </div>
              ))}
            </div>
          )}

          {/* Warnings */}
          {explanation.warnings.length > 0 && (
            <div className="space-y-1">
              {explanation.warnings.map((w, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2 text-xs text-accent-yellow"
                >
                  <AlertTriangle size={12} className="mt-0.5 shrink-0" />
                  <span>{w}</span>
                </div>
              ))}
            </div>
          )}

          {/* Technical (L3) — collapsible */}
          <details className="text-xs">
            <summary className="cursor-pointer text-text-secondary hover:text-text-primary transition-colors">
              Détails techniques
            </summary>
            <p className="mt-1 font-mono text-text-secondary bg-surface-hover rounded p-2 leading-relaxed">
              {explanation.technical}
            </p>
          </details>
        </div>
      )}
    </div>
  );
}
