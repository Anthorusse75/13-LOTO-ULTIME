import InfoTooltip from "@/components/common/InfoTooltip";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import PageIntro from "@/components/common/PageIntro";
import DrawBalls from "@/components/draws/DrawBalls";
import { useDraws } from "@/hooks/useDraws";
import { formatDate } from "@/utils/formatters";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";

const PAGE_SIZE = 50;

export default function DrawsPage() {
  const [page, setPage] = useState(0);
  const { data: draws, isLoading } = useDraws(page * PAGE_SIZE, PAGE_SIZE);

  if (isLoading) return <LoadingSpinner message="Chargement des tirages..." />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Historique des Tirages</h1>

      <PageIntro
        storageKey="draws"
        description="Cette page affiche l'ensemble des tirages officiels récupérés auprès de la FDJ (Française des Jeux). Ce sont les résultats réels qui alimentent tous les calculs du site. C'est comme un carnet de tous les tirages passés. Plus il y en a, plus nos analyses sont précises."
        tip="Le système récupère automatiquement les nouveaux tirages chaque nuit à 22h. Si vous venez de vous inscrire, les tirages sont en cours d'importation — revenez dans quelques minutes. Vous pouvez aussi déclencher l'import manuellement depuis la page Administration."
        terms={[
          {
            term: "Numéro de tirage",
            definition:
              "Identifiant officiel attribué par la FDJ. Par exemple, « #2024-087 » correspond au 87ème tirage de 2024. Vous pouvez le retrouver sur le site officiel fdj.fr.",
          },
          {
            term: "Numéros principaux",
            definition:
              "Les boules bleues : ce sont les numéros principaux tirés. Au Loto, il y en a 5 (parmi 49). À l'EuroMillions, il y en a 5 (parmi 50).",
          },
          {
            term: "Étoiles (EuroMillions)",
            definition:
              "Les boules jaunes à droite des numéros principaux. 2 étoiles tirées parmi 12. Pour gagner le jackpot, il faut les 5 numéros ET les 2 étoiles.",
          },
          {
            term: "Numéro chance (Loto)",
            definition:
              "La boule colorée supplémentaire au Loto FDJ. Tirée parmi 1 à 10. Permet de remporter des gains supplémentaires même sans avoir les 5 bons numéros.",
          },
        ]}
      />

      <div className="bg-surface rounded-lg border border-border overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-surface-hover">
              <th className="text-left px-4 py-3 text-text-secondary font-medium">
                <span className="flex items-center">
                  #<InfoTooltip text="Numéro officiel du tirage." />
                </span>
              </th>
              <th className="text-left px-4 py-3 text-text-secondary font-medium">
                <span className="flex items-center">
                  Date
                  <InfoTooltip text="Date à laquelle le tirage a eu lieu." />
                </span>
              </th>
              <th className="text-left px-4 py-3 text-text-secondary font-medium">
                <span className="flex items-center">
                  Numéros
                  <InfoTooltip text="Numéros tirés (+étoiles pour EuroMillions)." />
                </span>
              </th>
            </tr>
          </thead>
          <tbody>
            {draws && draws.length > 0 ? (
              draws.map((d) => (
                <tr
                  key={d.id}
                  className="border-b border-border hover:bg-surface-hover transition-colors"
                >
                  <td className="px-4 py-3 font-mono text-text-secondary">
                    {d.draw_number ?? d.id}
                  </td>
                  <td className="px-4 py-3 text-text-secondary">
                    {formatDate(d.draw_date)}
                  </td>
                  <td className="px-4 py-3">
                    <DrawBalls numbers={d.numbers} stars={d.stars} size="sm" />
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan={3}
                  className="px-4 py-8 text-center text-text-secondary"
                >
                  Aucun tirage disponible
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-center gap-4">
        <button
          onClick={() => setPage((p) => Math.max(0, p - 1))}
          disabled={page === 0}
          className="p-2 rounded-md hover:bg-surface-hover disabled:opacity-30 disabled:cursor-not-allowed text-text-secondary"
        >
          <ChevronLeft size={18} />
        </button>
        <span className="text-sm text-text-secondary">Page {page + 1}</span>
        <button
          onClick={() => setPage((p) => p + 1)}
          disabled={!draws || draws.length < PAGE_SIZE}
          className="p-2 rounded-md hover:bg-surface-hover disabled:opacity-30 disabled:cursor-not-allowed text-text-secondary"
        >
          <ChevronRight size={18} />
        </button>
      </div>
    </div>
  );
}
