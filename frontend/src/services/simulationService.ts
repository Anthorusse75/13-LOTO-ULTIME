import api from "./api";
import type {
  MonteCarloGridRequest,
  MonteCarloGridResponse,
  MonteCarloPortfolioRequest,
  MonteCarloPortfolioResponse,
  StabilityRequest,
  StabilityResponse,
  ComparisonRequest,
  ComparisonResponse,
} from "@/types/simulation";

export const simulationService = {
  monteCarlo: async (
    gameId: number,
    req: MonteCarloGridRequest
  ): Promise<MonteCarloGridResponse> => {
    const { data } = await api.post(`/games/${gameId}/simulation/monte-carlo`, req);
    return data;
  },

  monteCarloPortfolio: async (
    gameId: number,
    req: MonteCarloPortfolioRequest
  ): Promise<MonteCarloPortfolioResponse> => {
    const { data } = await api.post(
      `/games/${gameId}/simulation/monte-carlo/portfolio`,
      req
    );
    return data;
  },

  stability: async (
    gameId: number,
    req: StabilityRequest
  ): Promise<StabilityResponse> => {
    const { data } = await api.post(`/games/${gameId}/simulation/stability`, req);
    return data;
  },

  compareRandom: async (
    gameId: number,
    req: ComparisonRequest
  ): Promise<ComparisonResponse> => {
    const { data } = await api.post(`/games/${gameId}/simulation/compare-random`, req);
    return data;
  },
};
