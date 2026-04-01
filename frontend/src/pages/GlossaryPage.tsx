import { ArrowRight, Search } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

const glossaryTerms = [
  {
    term: "Cooccurrence",
    definition:
      "Mesure de la fréquence à laquelle deux numéros apparaissent ensemble dans un même tirage. Une forte cooccurrence indique une affinité historique.",
    seeAlso: { label: "Le scoring multicritère", to: "/how-it-works" },
  },
  {
    term: "Distance de Hamming",
    definition:
      "Nombre de positions où deux combinaisons diffèrent. Une distance de Hamming élevée entre deux grilles signifie une meilleure diversification.",
    seeAlso: {
      label: "Le portefeuille et la diversification",
      to: "/how-it-works",
    },
  },
  {
    term: "Écart (Gap)",
    definition:
      "Nombre de tirages écoulés depuis la dernière apparition d'un numéro. Un grand écart peut indiquer un numéro « froid ».",
    seeAlso: { label: "Le scoring multicritère", to: "/how-it-works" },
  },
  {
    term: "Entropie de Shannon",
    definition:
      "Mesure du désordre dans la distribution des numéros. Une entropie élevée signifie que les tirages sont proches d'une distribution uniforme.",
    seeAlso: { label: "Les probabilités et le hasard", to: "/how-it-works" },
  },
  {
    term: "Espérance de gain",
    definition:
      "Gain moyen théorique calculé par simulation Monte Carlo sur des milliers de tirages virtuels.",
    seeAlso: { label: "La simulation Monte Carlo", to: "/how-it-works" },
  },
  {
    term: "Fréquence observée",
    definition:
      "Proportion de tirages dans lesquels un numéro est apparu. Comparée à la fréquence théorique pour détecter les numéros chauds/froids.",
    seeAlso: { label: "Le scoring multicritère", to: "/how-it-works" },
  },
  {
    term: "Hill Climbing",
    definition:
      "Méthode d'optimisation locale qui améliore itérativement une solution en modifiant un numéro à la fois pour maximiser le score.",
    seeAlso: { label: "Les algorithmes d'optimisation", to: "/how-it-works" },
  },
  {
    term: "Inférence bayésienne",
    definition:
      "Méthode statistique qui met à jour la probabilité d'apparition de chaque numéro en combinant un a priori théorique avec les données observées.",
    seeAlso: { label: "Les probabilités et le hasard", to: "/how-it-works" },
  },
  {
    term: "Khi-deux (χ²)",
    definition:
      "Test statistique mesurant l'écart entre la distribution observée des numéros et la distribution théorique uniforme.",
  },
  {
    term: "Momentum",
    definition:
      "Pente de la régression linéaire des fréquences d'un numéro sur des fenêtres temporelles croissantes. Un momentum positif indique une tendance haussière.",
  },
  {
    term: "Monte Carlo",
    definition:
      "Méthode de simulation qui génère des milliers de tirages aléatoires pour estimer les gains et la performance d'une grille ou d'un portefeuille.",
    seeAlso: { label: "La simulation Monte Carlo", to: "/how-it-works" },
  },
  {
    term: "Pattern penalty",
    definition:
      "Pénalité appliquée aux combinaisons suivant des patterns trop prévisibles (suites consécutives, multiples d'un même nombre, etc.).",
    seeAlso: { label: "Le scoring multicritère", to: "/how-it-works" },
  },
  {
    term: "Portefeuille",
    definition:
      "Ensemble de grilles optimisées pour maximiser la couverture de numéros et la diversité tout en maintenant des scores élevés.",
    seeAlso: {
      label: "Le portefeuille et la diversification",
      to: "/how-it-works",
    },
  },
  {
    term: "Profil de jeu",
    definition:
      "Ensemble de pondérations prédéfinies pour les critères de scoring : équilibré, tendance, contrarian ou structurel.",
    seeAlso: { label: "Le scoring multicritère", to: "/how-it-works" },
  },
  {
    term: "R² (coefficient de détermination)",
    definition:
      "Mesure de la qualité de la régression linéaire pour le momentum. Un R² > 0.5 indique une tendance significative et fiable.",
  },
  {
    term: "Recuit simulé",
    definition:
      "Méta-heuristique inspirée de la métallurgie qui explore l'espace des solutions en acceptant parfois des dégradations pour échapper aux optimums locaux.",
    seeAlso: { label: "Les algorithmes d'optimisation", to: "/how-it-works" },
  },
  {
    term: "Recherche tabou",
    definition:
      "Méthode d'optimisation qui maintient une liste d'interdictions pour éviter de revisiter les solutions récemment explorées.",
    seeAlso: { label: "Les algorithmes d'optimisation", to: "/how-it-works" },
  },
  {
    term: "Scoring multicritère",
    definition:
      "Évaluation d'une grille sur 6 axes : fréquence, écart, cooccurrence, structure numérique, équilibre pairs/impairs-haut/bas, et pénalité pattern.",
    seeAlso: { label: "Le scoring multicritère", to: "/how-it-works" },
  },
  {
    term: "Système réduit (Wheeling)",
    definition:
      "Technique permettant de jouer plus de numéros que la grille standard ne l'autorise, en générant un ensemble optimisé de combinaisons avec un niveau de garantie minimum.",
    seeAlso: { label: "Les systèmes réduits (Wheeling)", to: "/how-it-works" },
  },
];

export default function GlossaryPage() {
  const [search, setSearch] = useState("");

  const filtered = glossaryTerms.filter(
    ({ term, definition }) =>
      term.toLowerCase().includes(search.toLowerCase()) ||
      definition.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-text-primary mb-2">Glossaire</h1>
      <p className="text-text-secondary mb-6">
        Définitions des termes techniques utilisés dans Loto Ultime.
      </p>

      <div className="relative mb-6">
        <Search
          size={16}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary"
        />
        <input
          type="text"
          placeholder="Rechercher un terme…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-9 pr-4 py-2 bg-surface border border-border rounded-lg text-sm text-text-primary placeholder:text-text-secondary focus:outline-none focus:ring-1 focus:ring-accent-blue"
        />
      </div>

      <div className="space-y-3">
        {filtered.map(({ term, definition, seeAlso }) => (
          <div
            key={term}
            className="p-4 bg-surface rounded-lg border border-border"
          >
            <dt className="font-semibold text-accent-blue mb-1">{term}</dt>
            <dd className="text-sm text-text-secondary leading-relaxed">
              {definition}
            </dd>
            {seeAlso && (
              <Link
                to={seeAlso.to}
                className="inline-flex items-center gap-1 mt-2 text-xs text-accent-blue hover:underline"
              >
                <ArrowRight size={12} />
                En savoir plus : {seeAlso.label}
              </Link>
            )}
          </div>
        ))}
        {filtered.length === 0 && (
          <p className="text-center text-text-secondary text-sm py-8">
            Aucun terme trouvé pour « {search} ».
          </p>
        )}
      </div>
    </div>
  );
}
