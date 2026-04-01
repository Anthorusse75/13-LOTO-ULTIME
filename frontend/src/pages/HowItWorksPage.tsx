import {
  BookOpen,
  Brain,
  ChevronDown,
  ChevronRight,
  Dices,
  FlaskConical,
  LineChart,
  Target,
} from "lucide-react";
import { useState } from "react";

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

interface LearnSectionProps {
  title: string;
  children: React.ReactNode;
}

function LearnSection({ title, children }: LearnSectionProps) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-border rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-2 px-4 py-3 bg-surface hover:bg-surface-hover transition-colors text-left"
        aria-expanded={open}
      >
        {open ? (
          <ChevronDown size={14} className="text-text-secondary shrink-0" />
        ) : (
          <ChevronRight size={14} className="text-text-secondary shrink-0" />
        )}
        <span className="text-sm font-semibold">{title}</span>
      </button>
      {open && (
        <div className="px-4 pb-4 pt-2 text-sm text-text-secondary leading-relaxed space-y-2">
          {children}
        </div>
      )}
    </div>
  );
}

export default function HowItWorksPage() {
  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
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
                <h3 className="font-semibold text-text-primary mb-1">
                  {title}
                </h3>
                <p className="text-sm text-text-secondary leading-relaxed">
                  {description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Pedagogy — Learn Sections */}
      <div>
        <h2 className="text-lg font-bold mb-4">Comprendre les concepts</h2>
        <div className="space-y-2">
          <LearnSection title="Les probabilités et le hasard">
            <p>
              La loterie est un jeu <strong>purement aléatoire</strong>. Chaque
              tirage est indépendant du précédent — les boules n'ont pas de
              mémoire. Statistiquement, toutes les combinaisons ont exactement
              la même probabilité d'être tirées.
            </p>
            <p>
              Alors pourquoi analyser ? Parce que le scoring mesure la
              <strong> qualité statistique</strong> d'une grille (équilibre,
              diversité), pas sa probabilité de gain. C'est comme choisir un bon
              cheval aux courses : on n'est pas sûr qu'il gagne, mais on peut
              évaluer ses chances objectivement.
            </p>
          </LearnSection>

          <LearnSection title="Le scoring multicritère">
            <p>
              Chaque grille est notée sur 6 critères indépendants pondérés. La
              note finale (0-10) est une moyenne pondérée. Les critères sont :
            </p>
            <ul className="list-disc pl-5 space-y-1">
              <li>
                <strong>Fréquence</strong> — les numéros sont-ils souvent sortis
                ?
              </li>
              <li>
                <strong>Écart (gap)</strong> — quand sont-ils sortis pour la
                dernière fois ?
              </li>
              <li>
                <strong>Co-occurrence</strong> — ces numéros sortent-ils souvent
                ensemble ?
              </li>
              <li>
                <strong>Structure</strong> — répartition par dizaines,
                terminaisons, somme.
              </li>
              <li>
                <strong>Équilibre</strong> — mix pair/impair, haut/bas.
              </li>
              <li>
                <strong>Pénalité pattern</strong> — malus pour les suites trop
                régulières.
              </li>
            </ul>
          </LearnSection>

          <LearnSection title="Les algorithmes d'optimisation">
            <p>
              Pour trouver les meilleures grilles parmi des millions de
              possibilités, on utilise des <strong>méta-heuristiques</strong> :
            </p>
            <ul className="list-disc pl-5 space-y-1">
              <li>
                <strong>Algorithme génétique</strong> — s'inspire de l'évolution
                darwinienne (sélection, croisement, mutation).
              </li>
              <li>
                <strong>Recuit simulé</strong> — imite le refroidissement des
                métaux pour éviter les minimums locaux.
              </li>
              <li>
                <strong>Recherche tabou</strong> — explore intelligemment en
                mémorisant les zones déjà visitées.
              </li>
              <li>
                <strong>Hill climbing</strong> — amélioration itérative simple
                et rapide.
              </li>
            </ul>
          </LearnSection>

          <LearnSection title="La simulation Monte Carlo">
            <p>
              On simule des milliers (voire des centaines de milliers) de
              tirages aléatoires fictifs et on regarde combien de fois vos
              numéros seraient sortis. Le résultat converge vers l'
              <strong>espérance mathématique</strong> (loi hypergéométrique).
            </p>
            <p>
              C'est utile pour vérifier que votre grille se comporte «
              normalement » et pour estimer la distribution de vos gains
              potentiels.
            </p>
          </LearnSection>

          <LearnSection title="Le portefeuille et la diversification">
            <p>
              Comme en finance, ne mettez pas tous vos œufs dans le même panier.
              Un <strong>portefeuille</strong> est un ensemble de grilles
              complémentaires qui maximisent la couverture numérique tout en
              gardant des scores individuels élevés.
            </p>
            <p>
              La <strong>distance de Hamming</strong> entre deux grilles compte
              le nombre de numéros différents. Plus cette distance est élevée,
              plus les grilles sont complémentaires.
            </p>
          </LearnSection>

          <LearnSection title="Les systèmes réduits (Wheeling)">
            <p>
              Un <strong>système réduit</strong> (ou <em>wheeling</em>) permet
              de jouer plus de numéros que ce que la grille standard autorise,
              tout en garantissant un niveau minimum de correspondance si
              certains de vos numéros sont tirés.
            </p>
            <p>
              <strong>Exemple concret :</strong> au Loto FDJ (5 numéros parmi
              49), si vous aimez 10 numéros, le système complet (toutes les
              combinaisons de 5 parmi 10) nécessiterait 252 grilles. Un système
              réduit avec <strong>garantie 3</strong> n'en nécessite qu'une
              dizaine — si 3 de vos numéros sont tirés, au moins une de vos
              grilles les contiendra.
            </p>
            <ul className="list-disc pl-5 space-y-1">
              <li>
                <strong>Paramètre t (garantie)</strong> — le nombre minimum de
                numéros que vous êtes sûr de retrouver dans une grille si t
                numéros parmi vos sélectionnés sont tirés.
              </li>
              <li>
                <strong>Couverture</strong> — pourcentage de combinaisons
                possibles couvertes par le système. 100% = système complet.
              </li>
              <li>
                <strong>Compromis</strong> — plus la garantie est élevée, plus
                il faut de grilles (et donc un budget plus important).
              </li>
            </ul>
            <p>
              La matrice de couverture montre quels numéros apparaissent dans
              quelles grilles. Les scénarios de gain conditionnels estiment vos
              gains potentiels selon le nombre de bons numéros.
            </p>
          </LearnSection>

          <LearnSection title="Comprendre le coût et les compromis">
            <p>
              Chaque grille a un coût fixe : <strong>2,20 €</strong> pour le
              Loto FDJ, <strong>2,50 €</strong> pour l'EuroMillions. Un système
              réduit de 15 grilles coûte donc entre 33 € et 37,50 €.
            </p>
            <p>
              <strong>La loi des rendements décroissants</strong> s'applique :
              augmenter le nombre de numéros sélectionnés ou le niveau de
              garantie augmente le coût de manière exponentielle, alors que le
              gain de couverture ralentit.
            </p>
            <ul className="list-disc pl-5 space-y-1">
              <li>
                <strong>Budget raisonnable</strong> — définissez un montant
                mensuel fixe que vous êtes prêt à dépenser et ne le dépassez
                jamais.
              </li>
              <li>
                <strong>Ratio coût/couverture</strong> — comparez le pourcentage
                de couverture obtenu pour chaque euro dépensé. L'optimiseur
                budget vous aide à trouver le meilleur rapport.
              </li>
              <li>
                <strong>Espérance conditionnelle</strong> — le gain espéré «si
                vous avez N bons numéros» permet d'évaluer le rapport
                risque/bénéfice de chaque système.
              </li>
            </ul>
            <p>
              L'outil Budget intelligent analyse automatiquement ces compromis
              et propose la stratégie optimale pour votre enveloppe.
            </p>
          </LearnSection>

          <LearnSection title="Jeu responsable">
            <p>
              La loterie reste un jeu de hasard.{" "}
              <strong>Aucun outil ne garantit un gain</strong>. Loto Ultime vous
              aide à faire des choix plus informés, pas à prédire l'avenir.
              Fixez-vous un budget mensuel et ne le dépassez jamais. Si le jeu
              n'est plus un plaisir, consultez{" "}
              <a
                href="https://www.joueurs-info-service.fr/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-accent-blue underline"
              >
                Joueurs Info Service
              </a>
              .
            </p>
          </LearnSection>
        </div>
      </div>

      <div className="p-4 bg-accent-amber/10 border border-accent-amber/30 rounded-lg">
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
