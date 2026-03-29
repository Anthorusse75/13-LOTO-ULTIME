import type {
  BayesianItem,
  CooccurrenceResponse,
  DistributionResponse,
  FrequencyItem,
  GapItem,
  GraphResponse,
  StatisticsResponse,
  TemporalResponse,
} from "@/types/statistics";
import api from "./api";

export const statisticsService = {
  getAll: async (gameId: number): Promise<StatisticsResponse> => {
    const { data } = await api.get(`/games/${gameId}/statistics`);
    return data;
  },

  getFrequencies: async (
    gameId: number,
    lastN?: number,
  ): Promise<FrequencyItem[]> => {
    const params = lastN ? { last_n: lastN } : {};
    const { data } = await api.get(`/games/${gameId}/statistics/frequencies`, {
      params,
    });
    return data;
  },

  getGaps: async (gameId: number, lastN?: number): Promise<GapItem[]> => {
    const params = lastN ? { last_n: lastN } : {};
    const { data } = await api.get(`/games/${gameId}/statistics/gaps`, {
      params,
    });
    return data;
  },

  getCooccurrences: async (gameId: number): Promise<CooccurrenceResponse> => {
    const { data } = await api.get(`/games/${gameId}/statistics/cooccurrences`);
    return data;
  },

  getTemporal: async (gameId: number): Promise<TemporalResponse> => {
    const { data } = await api.get(`/games/${gameId}/statistics/temporal`);
    return data;
  },

  getDistribution: async (gameId: number): Promise<DistributionResponse> => {
    const { data } = await api.get(`/games/${gameId}/statistics/distribution`);
    return data;
  },

  getBayesian: async (gameId: number): Promise<BayesianItem[]> => {
    const { data } = await api.get(`/games/${gameId}/statistics/bayesian`);
    return data;
  },

  getGraph: async (gameId: number): Promise<GraphResponse> => {
    const { data } = await api.get(`/games/${gameId}/statistics/graph`);
    return data;
  },

  recompute: async (gameId: number): Promise<StatisticsResponse> => {
    const { data } = await api.post(`/games/${gameId}/statistics/recompute`);
    return data;
  },
};
