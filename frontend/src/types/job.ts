export type JobStatus =
  | "PENDING"
  | "RUNNING"
  | "SUCCESS"
  | "FAILED"
  | "CANCELLED";

export interface JobExecution {
  id: number;
  job_name: string;
  game_id: number | null;
  status: JobStatus;
  started_at: string;
  finished_at: string | null;
  duration_seconds: number | null;
  result_summary: Record<string, unknown> | null;
  error_message: string | null;
  triggered_by: string;
}

export interface SchedulerStatus {
  running_jobs: string[];
  running_count: number;
  last_runs: Record<
    string,
    {
      status: string;
      started_at: string;
      finished_at: string | null;
      duration_seconds: number | null;
    }
  >;
}
