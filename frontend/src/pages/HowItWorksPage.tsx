import { BookOpen, Brain, Dices, FlaskConical, LineChart, Target } from "lucide-react";

const steps = [
  {
    icon: Dices,
    title: "1. Collecte des tirages",
    description:
      "Le système récupère automatiquement les résultats officiels des tirages Loto FDJ et EuroMillions depuis les sources publiques.",
  },
  {
    icon: LineChart,
    title: "2. Analyse statistique",
    description:
      "Sept moteurs statistiques analysent les données : fréquences, écarts, cooccurrences, tendances temporelles, distributions, analyse bayésienne et graphes de relations.",
  },
  {
    icon: Brain,
    title: "3. Scoring multicritère",
    description:
      "Chaque combinaison est évaluée sur 6 critères pondérés (fréquence, écart, cooccurrence, structure, équilibre, pénalité pattern) selon un profil de jeu choisi.",
  },
  {
    icon: Target,
    title: "4. Optimisation méta-heuristique",
    description:
      "Des algorithmes avancés (recuit simulé, algorithme génétique, recherche tabou, hill climbing) génèrent les meilleures combinaisons possibles.",
  },
  {
    icon: FlaskConical,
    title: "5. Simulation Monte Carlo",
    description:
      "Les grilles sont évaluées via des milliers de simulations pour estimer leur espérance de gain, leur stabilité et leur performance relative.",
  },
  {
    icon: BookOpen,
    title: "6. Portefeuille optimisé",
    description:
      "Un algorithme de diversification sélectionne les grilles les plus performantes tout en maximisant la couverture et la distance de Hamming entre elles.",
  },
];

export default function HowItWorksPage() {
  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-text-primary mb-2">
        Comment ça marche ?
      </h1>
      <p className="text-text-secondary mb-8">
        Loto Ultime utilise des techniques avancées d'analyse statistique et
        d'optimisation pour vous aider à choisir vos combinaisons. Voici les
        étapes du processus.
      </p>

      <div className="space-y-6">
        {steps.map(({ icon: Icon, title, description }) => (
          <div
            key={title}
            className="flex gap-4 p-4 bg-surface rounded-lg border border-border"
          >
            <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-accent-blue/10 flex items-center justify-center">
              <Icon size={20} className="text-accent-blue" />
            </div>
            <div>
              <h3 className="font-semibold text-text-primary mb-1">{title}</h3>
              <p className="text-sm text-text-secondary leading-relaxed">
                {description}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 p-4 bg-accent-amber/10 border border-accent-amber/30 rounded-lg">
        <p className="text-sm text-text-secondary">
          <strong className="text-accent-amber">⚠ Rappel :</strong> Aucun
          système ne peut prédire les résultats d'un tirage aléatoire. Loto
          Ultime est un outil d'aide à la décision basé sur des analyses
          historiques. Jouez de manière responsable.
        </p>
      </div>
    </div>
  );
}
