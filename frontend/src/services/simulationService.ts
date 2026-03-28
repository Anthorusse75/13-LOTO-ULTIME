import type {
  ComparisonRequest,
  ComparisonResponse,
  MonteCarloGridRequest,
  MonteCarloGridResponse,
  MonteCarloPortfolioRequest,
  MonteCarloPortfolioResponse,
  StabilityRequest,
  StabilityResponse,
} from "@/types/simulation";
import api from "./api";

export const simulationService = {
  monteCarlo: async (
    gameId: number,
    req: MonteCarloGridRequest,
  ): Promise<MonteCarloGridResponse> => {
    const { data } = await api.post(
      `/games/${gameId}/simulation/monte-carlo`,
      req,
      { timeout: 120_000 },
    );
    return data;
  },

  monteCarloPortfolio: async (
    gameId: number,
    req: MonteCarloPortfolioRequest,
  ): Promise<MonteCarloPortfolioResponse> => {
    const { data } = await api.post(
      `/games/${gameId}/simulation/monte-carlo/portfolio`,
      req,
      { timeout: 120_000 },
    );
    return data;
  },

  stability: async (
    gameId: number,
    req: StabilityRequest,
  ): Promise<StabilityResponse> => {
    const { data } = await api.post(
      `/games/${gameId}/simulation/stability`,
      req,
      { timeout: 120_000 },
    );
    return data;
  },

  compareRandom: async (
    gameId: number,
    req: ComparisonRequest,
  ): Promise<ComparisonResponse> => {
    const { data } = await api.post(
      `/games/${gameId}/simulation/compare-random`,
      req,
      { timeout: 120_000 },
    );
    return data;
  },
};
