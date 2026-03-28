import type { JobExecution, SchedulerStatus } from "@/types/job";
import api from "./api";

export const jobService = {
  getAll: async (limit = 50, offset = 0): Promise<JobExecution[]> => {
    const { data } = await api.get("/jobs/", { params: { limit, offset } });
    return data;
  },

  getStatus: async (): Promise<SchedulerStatus> => {
    const { data } = await api.get("/jobs/status");
    return data;
  },

  getHistory: async (
    jobName: string,
    limit = 20,
  ): Promise<JobExecution[]> => {
    const { data } = await api.get(`/jobs/${jobName}/history`, {
      params: { limit },
    });
    return data;
  },

  trigger: async (jobName: string): Promise<JobExecution> => {
    const { data } = await api.post(`/jobs/${jobName}/trigger`);
    return data;
  },
};
