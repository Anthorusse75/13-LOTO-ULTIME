/**
 * PageIntro — contextual tip always visible + collapsible terms/description.
 * Tip is always shown as a banner to guide the user.
 * Description and terms are hidden in a collapsible section.
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

export default function PageIntro({
  storageKey,
  description,
  terms,
  tip,
}: PageIntroProps) {
  const [open, setOpen] = useState(() => isOpenStored(storageKey));

  function toggle() {
    const next = !open;
    setOpen(next);
    setOpenStored(storageKey, next);
  }

  return (
    <div className="space-y-2">
      {/* Tip — ALWAYS visible */}
      {tip && (
        <div className="flex items-start gap-2.5 bg-accent-yellow/10 border border-accent-yellow/25 rounded-lg px-4 py-3">
          <Lightbulb size={15} className="text-accent-yellow mt-0.5 shrink-0" />
          <p className="text-sm text-text-primary leading-relaxed">{tip}</p>
        </div>
      )}

      {/* Collapsible section for description + terms */}
      <div className="border border-border/50 rounded-lg overflow-hidden">
        <button
          onClick={toggle}
          className="w-full flex items-center justify-between px-4 py-2 bg-surface-hover/50 hover:bg-surface-hover transition-colors text-left"
          aria-expanded={open}
        >
          <span className="flex items-center gap-2 text-xs text-text-secondary">
            <HelpCircle size={13} />
            Explications et termes clés
          </span>
          {open ? (
            <ChevronUp size={13} className="text-text-secondary shrink-0" />
          ) : (
            <ChevronDown size={13} className="text-text-secondary shrink-0" />
          )}
        </button>

        {open && (
          <div className="px-4 py-4 space-y-4 border-t border-border/50">
            {/* Description */}
            <p className="text-sm text-text-secondary leading-relaxed">
              {description}
            </p>

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
                      <p className="text-xs font-semibold text-text-primary">
                        {t.term}
                      </p>
                      <p className="text-xs text-text-secondary">
                        {t.definition}
                      </p>
                      {t.strength && (
                        <p className="text-xs text-accent-green">
                          ✓ {t.strength}
                        </p>
                      )}
                      {t.limit && (
                        <p className="text-xs text-accent-yellow">
                          ⚠ {t.limit}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
