import { useSettingsStore } from "@/stores/settingsStore";
import { Bot, ChevronDown, ChevronUp, Lightbulb, X } from "lucide-react";
import { useMemo, useState } from "react";
import { useLocation } from "react-router-dom";

// ─── Contextual advice per page ───────────────────────────────────────────────
type Tip = { icon: string; text: string };

const PAGE_TIPS: Record<string, { title: string; tips: Tip[] }> = {
  "/": {
    title: "Tableau de bord",
    tips: [
      {
        icon: "📊",
        text: "Consultez les KPIs pour un aperçu rapide de la santé du pipeline.",
      },
      {
        icon: "🎯",
        text: "Le top 3 des grilles est recalculé chaque soir à 22h automatiquement.",
      },
      {
        icon: "⚡",
        text: "Si la dernière exécution du pipeline est trop ancienne, relancez-la depuis l'Admin.",
      },
    ],
  },
  "/draws": {
    title: "Tirages",
    tips: [
      {
        icon: "🔄",
        text: "Les tirages sont importés automatiquement chaque soir. Aucune action requise.",
      },
      {
        icon: "📅",
        text: "Utilisez le filtre de période pour analyser une fenêtre temporelle spécifique.",
      },
      {
        icon: "⭐",
        text: "Pour EuroMillions, les étoiles sont affichées en jaune à la droite des numéros.",
      },
    ],
  },
  "/statistics": {
    title: "Statistiques",
    tips: [
      {
        icon: "📈",
        text: "L'onglet Fréquences révèle les numéros sur-représentés vs sous-représentés.",
      },
      {
        icon: "⏱️",
        text: "Un écart élevé (rouge) indique un numéro « en retard » — potentiellement intéressant.",
      },
      {
        icon: "🧪",
        text: "L'onglet Bayésien fournit des intervalles de confiance sur les probabilités réelles.",
      },
      {
        icon: "⭐",
        text: "L'onglet Étoiles / Numéros Chance contient les statistiques des numéros complémentaires.",
      },
    ],
  },
  "/grids": {
    title: "Grilles",
    tips: [
      {
        icon: "🎲",
        text: "Le profil 'Contrarian' favorise les numéros en retard — plus risqué mais potentiellement plus diversifié.",
      },
      {
        icon: "💡",
        text: "Générez 5–10 grilles avec des profils différents, puis marquez vos favorites.",
      },
      {
        icon: "📤",
        text: "Exportez vos grilles en PDF avant de jouer pour garder une trace.",
      },
      {
        icon: "❤️",
        text: "Utilisez les favoris pour ne conserver que les meilleures grilles entre deux sessions.",
      },
    ],
  },
  "/portfolio": {
    title: "Portefeuille",
    tips: [
      {
        icon: "🎯",
        text: "La stratégie 'Équilibre' optimise le rapport couverture/coût — idéale pour débuter.",
      },
      {
        icon: "📊",
        text: "La stratégie 'Max diversité' minimise les recoupements entre grilles.",
      },
      {
        icon: "💰",
        text: "N'investissez jamais plus que vous ne pouvez vous permettre de perdre.",
      },
    ],
  },
  "/simulation": {
    title: "Simulation",
    tips: [
      {
        icon: "🔬",
        text: "Monte Carlo sur 10 000 itérations donne une estimation fiable du ROI attendu.",
      },
      {
        icon: "📉",
        text: "Un ROI négatif est normal — la loterie est conçue pour l'opérateur, pas le joueur.",
      },
      {
        icon: "⚖️",
        text: "La comparaison A/B vous permet de choisir entre deux stratégies d'optimisation.",
      },
      {
        icon: "🎯",
        text: "Comparez votre grille avec une grille aléatoire pour mesurer l'apport des statistiques.",
      },
    ],
  },
  "/history": {
    title: "Historique",
    tips: [
      {
        icon: "✅",
        text: "Marquez vos grilles comme 'jouées' pour suivre vos performances réelles.",
      },
      {
        icon: "📊",
        text: "Le graphique cumulatif vous montre l'évolution de vos gains/pertes dans le temps.",
      },
      {
        icon: "🔍",
        text: "Comparez vos grilles jouées avec le meilleur tirage correspondant pour évaluer votre score.",
      },
    ],
  },
  "/favorites": {
    title: "Favoris",
    tips: [
      {
        icon: "❤️",
        text: "Vos grilles favorites sont disponibles même après re-génération du portfolio.",
      },
      {
        icon: "📤",
        text: "Exportez vos favoris en PDF avec scores et justifications détaillées.",
      },
    ],
  },
  "/admin": {
    title: "Administration",
    tips: [
      {
        icon: "⚠️",
        text: "Le recalcul complet peut prendre 30s–2min selon le volume de tirages.",
      },
      {
        icon: "🔒",
        text: "Seuls les comptes ADMIN peuvent déclencher des jobs manuellement.",
      },
      {
        icon: "📋",
        text: "L'historique des jobs vous permet de diagnostiquer les erreurs de pipeline.",
      },
    ],
  },
};

const DEFAULT_TIPS = {
  title: "Conseil",
  tips: [
    {
      icon: "ℹ️",
      text: "Naviguez dans le menu pour explorer toutes les fonctionnalités.",
    },
  ],
};

// ─── Component ────────────────────────────────────────────────────────────────
export default function AiCoach() {
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [dismissed, setDismissed] = useState(false);
  const coachEnabled = useSettingsStore((s) => s.coachEnabled ?? true);

  const context = useMemo(() => {
    const path = "/" + location.pathname.split("/")[1];
    return PAGE_TIPS[path] ?? DEFAULT_TIPS;
  }, [location.pathname]);

  if (!coachEnabled || dismissed) return null;

  return (
    <div
      className="fixed bottom-4 right-4 z-40 w-80 shadow-xl rounded-xl border border-border bg-surface text-text-primary"
      role="complementary"
      aria-label="Conseiller IA"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-accent-blue/10 rounded-t-xl border-b border-border">
        <button
          className="flex items-center gap-2 flex-1 text-left"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          aria-controls="ai-coach-body"
        >
          <Bot className="w-4 h-4 text-accent-blue shrink-0" aria-hidden="true" />
          <span className="font-semibold text-sm">Coach — {context.title}</span>
          {open ? (
            <ChevronDown
              className="w-4 h-4 ml-auto text-text-secondary"
              aria-hidden="true"
            />
          ) : (
            <ChevronUp
              className="w-4 h-4 ml-auto text-text-secondary"
              aria-hidden="true"
            />
          )}
        </button>
        <button
          onClick={() => setDismissed(true)}
          className="ml-2 text-text-secondary hover:text-text-primary transition-colors"
          aria-label="Fermer le coach"
        >
          <X className="w-4 h-4" aria-hidden="true" />
        </button>
      </div>

      {/* Body */}
      {open && (
        <div id="ai-coach-body" className="px-4 py-3 space-y-2.5" role="list">
          {context.tips.map((tip, i) => (
            <div
              key={i}
              className="flex gap-2.5 items-start text-sm"
              role="listitem"
            >
              <span
                className="text-base leading-none mt-0.5"
                aria-hidden="true"
              >
                {tip.icon}
              </span>
              <span className="text-text-secondary leading-snug">
                {tip.text}
              </span>
            </div>
          ))}
          <div className="pt-1 border-t border-border">
            <span className="flex items-center gap-1 text-xs text-text-secondary">
              <Lightbulb className="w-3 h-3" aria-hidden="true" />
              Conseils basés sur la page active
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
