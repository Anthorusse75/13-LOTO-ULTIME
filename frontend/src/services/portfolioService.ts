import api from "./api";
import type {
  PortfolioGenerateRequest,
  PortfolioGenerateResponse,
} from "@/types/portfolio";

export const portfolioService = {
  generate: async (
    gameId: number,
    req: PortfolioGenerateRequest
  ): Promise<PortfolioGenerateResponse> => {
    const { data } = await api.post(`/games/${gameId}/portfolios/generate`, req);
    return data;
  },
};
