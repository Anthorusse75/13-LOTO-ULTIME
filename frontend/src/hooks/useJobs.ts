import { jobService } from "@/services/jobService";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

export function useJobs(limit = 50) {
  return useQuery({
    queryKey: ["jobs", limit],
    queryFn: () => jobService.getAll(limit),
    staleTime: 30 * 1000,
    refetchInterval: 15 * 1000,
  });
}

export function useSchedulerStatus() {
  return useQuery({
    queryKey: ["jobs", "status"],
    queryFn: () => jobService.getStatus(),
    staleTime: 15 * 1000,
    refetchInterval: 15 * 1000,
  });
}

export function useTriggerJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (jobName: string) => jobService.trigger(jobName),
    onSuccess: (_data, jobName) => {
      toast.success(`Job "${jobName}" lancé avec succès`);
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
  });
}
