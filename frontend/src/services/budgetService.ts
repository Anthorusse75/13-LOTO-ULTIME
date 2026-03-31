import type {
  BudgetOptimizeRequest,
  BudgetOptimizeResponse,
  BudgetPlanResponse,
} from "@/types/budget";
import api from "./api";

export const budgetService = {
  optimize: async (
    gameId: number,
    req: BudgetOptimizeRequest,
  ): Promise<BudgetOptimizeResponse> => {
    const { data } = await api.post(`/games/${gameId}/budget/optimize`, req, {
      timeout: 120_000,
    });
    return data;
  },

  getHistory: async (gameId: number): Promise<BudgetPlanResponse[]> => {
    const { data } = await api.get(`/games/${gameId}/budget/history`);
    return data;
  },

  getById: async (
    gameId: number,
    planId: number,
  ): Promise<BudgetPlanResponse> => {
    const { data } = await api.get(`/games/${gameId}/budget/${planId}`);
    return data;
  },

  delete: async (gameId: number, planId: number): Promise<void> => {
    await api.delete(`/games/${gameId}/budget/${planId}`);
  },
};
