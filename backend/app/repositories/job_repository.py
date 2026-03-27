from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import JobExecution, JobStatus

from .base import BaseRepository


class JobRepository(BaseRepository[JobExecution]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, JobExecution)

    async def get_running_jobs(self) -> list[JobExecution]:
        stmt = (
            select(JobExecution)
            .where(JobExecution.status == JobStatus.RUNNING)
            .order_by(JobExecution.started_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_by_name(self, job_name: str) -> JobExecution | None:
        stmt = (
            select(JobExecution)
            .where(JobExecution.job_name == job_name)
            .order_by(JobExecution.started_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
