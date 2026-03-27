from datetime import datetime

from pydantic import BaseModel

from app.models.job import JobStatus


class JobExecutionResponse(BaseModel):
    id: int
    job_name: str
    game_id: int | None
    status: JobStatus
    started_at: datetime
    finished_at: datetime | None
    duration_seconds: float | None
    result_summary: dict | None
    error_message: str | None
    triggered_by: str

    model_config = {"from_attributes": True}
