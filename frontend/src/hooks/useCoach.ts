import {
  getAnalysis,
  getCoachAdvice,
  getGridAnalysis,
} from "@/services/coachService";
import { useMutation } from "@tanstack/react-query";

export function useCoachAdvice() {
  return useMutation({
    mutationFn: getCoachAdvice,
  });
}

export function useGridAnalysis() {
  return useMutation({
    mutationFn: getGridAnalysis,
  });
}

export function useAiAnalysis() {
  return useMutation({
    mutationFn: getAnalysis,
  });
}
