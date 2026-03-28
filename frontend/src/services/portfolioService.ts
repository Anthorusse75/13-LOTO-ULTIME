import type {
  PortfolioGenerateRequest,
  PortfolioGenerateResponse,
} from "@/types/portfolio";
import api from "./api";

export const portfolioService = {
  generate: async (
    gameId: number,
    req: PortfolioGenerateRequest,
  ): Promise<PortfolioGenerateResponse> => {
    const { data } = await api.post(
      `/games/${gameId}/portfolios/generate`,
      req,
      { timeout: 120_000 },
    );
    return data;
  },

  deletePortfolio: async (
    gameId: number,
    portfolioId: number,
  ): Promise<void> => {
    await api.delete(`/games/${gameId}/portfolios/${portfolioId}`);
  },
};
