import { useSettingsStore } from "@/stores/settingsStore";
import { ArrowRight, CheckCircle, X } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

type Step = {
  title: string;
  description: string;
  icon: string;
  action?: { label: string; to: string };
};

const STEPS: Step[] = [
  {
    title: "Bienvenue sur LOTO ULTIME ! 🎉",
    description:
      "LOTO ULTIME analyse statistiquement les tirages historiques pour vous aider à construire des grilles informées. Ce tour rapide vous guidera à travers les fonctionnalités clés.",
    icon: "🚀",
  },
  {
    title: "Les Tirages",
    description:
      "L'historique complet des tirages EuroMillions et Loto FDJ est importé automatiquement chaque soir à 22h. Aucune saisie manuelle requise.",
    icon: "🎲",
    action: { label: "Voir les tirages", to: "/draws" },
  },
  {
    title: "Les Statistiques",
    description:
      "7 onglets d'analyse : fréquences, écarts, co-occurrences, tendances temporelles, distributions, analyse bayésienne, et graphe de corrélations.",
    icon: "📊",
    action: { label: "Explorer les stats", to: "/statistics" },
  },
  {
    title: "La Génération de Grilles",
    description:
      "4 profils disponibles (Équilibre, Tendance, Contrarian, Structurel) combinés à 4 algorithmes d'optimisation (SA, GA, Tabu, Hill Climbing). Chaque grille est scorée sur 6 critères.",
    icon: "🎯",
    action: { label: "Générer des grilles", to: "/grids" },
  },
  {
    title: "Le Portefeuille",
    description:
      "Optimisez un ensemble de grilles pour maximiser la couverture tout en minimisant les recoupements. 4 stratégies de portfolio disponibles.",
    icon: "💼",
    action: { label: "Créer un portefeuille", to: "/portfolio" },
  },
  {
    title: "La Simulation Monte Carlo",
    description:
      "Simulez des milliers de tirages pour estimer le ROI attendu de vos grilles. Comparez deux stratégies en mode A/B pour choisir la meilleure.",
    icon: "🔬",
    action: { label: "Lancer une simulation", to: "/simulation" },
  },
  {
    title: "Vous êtes prêt(e) ! ✅",
    description:
      "Le Coach IA (en bas à droite) vous donnera des conseils contextuels sur chaque page. Commencez par consulter les statistiques pour comprendre les tendances actuelles.",
    icon: "🎓",
    action: { label: "Voir le tableau de bord", to: "/" },
  },
];

export default function OnboardingTour() {
  const [step, setStep] = useState(0);
  const [visible, setVisible] = useState(false);
  const onboardingDone = useSettingsStore((s) => s.onboardingDone);
  const setOnboardingDone = useSettingsStore((s) => s.setOnboardingDone);
  const navigate = useNavigate();

  // Show tour only on first visit
  useEffect(() => {
    if (!onboardingDone) {
      // Small delay so the app has time to render
      const t = setTimeout(() => setVisible(true), 800);
      return () => clearTimeout(t);
    }
  }, [onboardingDone]);

  const handleDismiss = () => {
    setVisible(false);
    setOnboardingDone(true);
  };

  const handleNext = () => {
    if (step < STEPS.length - 1) {
      setStep((s) => s + 1);
    } else {
      handleDismiss();
    }
  };

  const handleAction = (to: string) => {
    navigate(to);
    handleNext();
  };

  if (!visible) return null;

  const current = STEPS[step];
  const isLast = step === STEPS.length - 1;

  return (
    /* Backdrop */
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="onboarding-title"
      aria-describedby="onboarding-desc"
    >
      <div className="relative w-full max-w-md mx-4 bg-surface text-text-primary rounded-2xl shadow-2xl border border-border p-6">
        {/* Close */}
        <button
          onClick={handleDismiss}
          className="absolute top-4 right-4 text-text-secondary hover:text-text-primary transition-colors"
          aria-label="Fermer le tour de présentation"
        >
          <X className="w-5 h-5" aria-hidden="true" />
        </button>

        {/* Step indicator */}
        <div
          className="flex gap-1.5 mb-6"
          role="tablist"
          aria-label="Étapes du tutoriel"
        >
          {STEPS.map((_, i) => (
            <div
              key={i}
              role="tab"
              aria-selected={i === step}
              aria-label={`Étape ${i + 1}`}
              className={`h-1.5 flex-1 rounded-full transition-colors ${
                i <= step ? "bg-accent-blue" : "bg-surface-hover"
              }`}
            />
          ))}
        </div>

        {/* Icon + Title */}
        <div className="text-4xl mb-3 text-center" aria-hidden="true">
          {current.icon}
        </div>
        <h2
          id="onboarding-title"
          className="text-xl font-bold text-center mb-3"
        >
          {current.title}
        </h2>
        <p
          id="onboarding-desc"
          className="text-text-secondary text-sm text-center leading-relaxed mb-6"
        >
          {current.description}
        </p>

        {/* Actions */}
        <div className="flex flex-col gap-2">
          {current.action && (
            <button
              onClick={() => handleAction(current.action!.to)}
              className="flex items-center justify-center gap-2 w-full px-4 py-2.5 rounded-lg bg-accent-blue text-white font-medium text-sm hover:bg-accent-blue/90 transition-colors"
            >
              {current.action.label}
              <ArrowRight className="w-4 h-4" aria-hidden="true" />
            </button>
          )}
          <button
            onClick={handleNext}
            className="flex items-center justify-center gap-2 w-full px-4 py-2 rounded-lg border border-border text-sm text-text-secondary hover:text-text-primary hover:border-accent-blue/50 transition-colors"
          >
            {isLast ? (
              <>
                <CheckCircle
                  className="w-4 h-4 text-green-500"
                  aria-hidden="true"
                />
                Terminer
              </>
            ) : (
              <>
                Suivant
                <ArrowRight className="w-4 h-4" aria-hidden="true" />
              </>
            )}
          </button>
        </div>

        {/* Counter */}
        <p className="text-xs text-text-secondary text-center mt-4">
          Étape {step + 1} / {STEPS.length}
        </p>
      </div>
    </div>
  );
}
