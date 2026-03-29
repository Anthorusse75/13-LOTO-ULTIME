/**
 * PageIntro — collapsible help accordion shown at the top of each main page.
 * Defaults to collapsed. State persisted in localStorage per storageKey.
 */
import { ChevronDown, ChevronUp, HelpCircle, Lightbulb } from "lucide-react";
import { useState } from "react";

interface Term {
  term: string;
  definition: string;
  strength?: string;
  limit?: string;
}

interface PageIntroProps {
  storageKey: string;
  description: string;
  terms?: Term[];
  tip?: string;
}

function isOpenStored(key: string): boolean {
  try {
    return localStorage.getItem(`page-intro-open:${key}`) === "1";
  } catch {
    return false;
  }
}

function setOpenStored(key: string, val: boolean) {
  try {
    if (val) {
      localStorage.setItem(`page-intro-open:${key}`, "1");
    } else {
      localStorage.removeItem(`page-intro-open:${key}`);
    }
  } catch {
    // ignore
  }
}

export default function PageIntro({ storageKey, description, terms, tip }: PageIntroProps) {
  const [open, setOpen] = useState(() => isOpenStored(storageKey));

  function toggle() {
    const next = !open;
    setOpen(next);
    setOpenStored(storageKey, next);
  }

  return (
    <div className="border border-accent-blue/20 rounded-lg overflow-hidden">
      {/* Header — always visible */}
      <button
        onClick={toggle}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-accent-blue/5 hover:bg-accent-blue/10 transition-colors text-left"
        aria-expanded={open}
      >
        <span className="flex items-center gap-2 text-sm font-medium text-accent-blue">
          <HelpCircle size={14} />
          À propos de cette page
        </span>
        {open ? (
          <ChevronUp size={14} className="text-accent-blue shrink-0" />
        ) : (
          <ChevronDown size={14} className="text-text-secondary shrink-0" />
        )}
      </button>

      {/* Expandable content */}
      {open && (
        <div className="px-4 py-4 space-y-4 bg-accent-blue/5 border-t border-accent-blue/15">
          {/* Description */}
          <p className="text-sm text-text-primary leading-relaxed">{description}</p>

          {/* Terms */}
          {terms && terms.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-text-secondary uppercase tracking-wide mb-2">
                Termes clés
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {terms.map((t) => (
                  <div
                    key={t.term}
                    className="bg-surface rounded-md border border-border px-3 py-2 space-y-0.5"
                  >
                    <p className="text-xs font-semibold text-text-primary">{t.term}</p>
                    <p className="text-xs text-text-secondary">{t.definition}</p>
                    {t.strength && (
                      <p className="text-xs text-accent-green">✓ {t.strength}</p>
                    )}
                    {t.limit && (
                      <p className="text-xs text-accent-yellow">⚠ {t.limit}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tip */}
          {tip && (
            <div className="flex items-start gap-2 bg-accent-yellow/10 border border-accent-yellow/20 rounded-md px-3 py-2">
              <Lightbulb size={13} className="text-accent-yellow mt-0.5 shrink-0" />
              <p className="text-xs text-text-primary">{tip}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
