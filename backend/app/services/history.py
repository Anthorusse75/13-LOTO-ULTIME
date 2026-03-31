"""History service — save, list, detail, duplicate, delete user results."""

import math
from datetime import UTC, datetime
from typing import Any

from app.models.saved_result import UserSavedResult
from app.repositories.saved_result_repository import SavedResultRepository

VALID_RESULT_TYPES = {"grid", "portfolio", "wheeling", "budget_plan", "comparison", "simulation"}


class HistoryService:
    def __init__(self, repo: SavedResultRepository) -> None:
        self.repo = repo

    async def save_result(
        self,
        user_id: int,
        result_type: str,
        parameters: dict[str, Any],
        result_data: dict[str, Any],
        game_id: int | None = None,
        name: str | None = None,
        tags: list[str] | None = None,
    ) -> UserSavedResult:
        if result_type not in VALID_RESULT_TYPES:
            raise ValueError(f"Invalid result_type: {result_type}")
        result = UserSavedResult(
            user_id=user_id,
            game_id=game_id,
            result_type=result_type,
            name=name,
            parameters=parameters,
            result_data=result_data,
            tags=tags or [],
        )
        return await self.repo.create(result)

    async def list_results(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 50,
        result_type: str | None = None,
        is_favorite: bool | None = None,
    ) -> dict[str, Any]:
        offset = (page - 1) * page_size
        total = await self.repo.count_by_user(user_id, result_type, is_favorite)
        items = await self.repo.list_by_user(user_id, offset, page_size, result_type, is_favorite)
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": math.ceil(total / page_size) if total > 0 else 0,
        }

    async def get_result(self, result_id: int, user_id: int) -> UserSavedResult | None:
        return await self.repo.get_by_user(result_id, user_id)

    async def delete_result(self, result_id: int, user_id: int) -> bool:
        return await self.repo.delete(result_id, user_id)

    async def duplicate_result(self, result_id: int, user_id: int) -> UserSavedResult | None:
        original = await self.repo.get_by_user(result_id, user_id)
        if original is None:
            return None
        copy = UserSavedResult(
            user_id=user_id,
            game_id=original.game_id,
            result_type=original.result_type,
            name=f"{original.name or 'Sans nom'} (copie)" if original.name else "Copie",
            parameters=original.parameters,
            result_data=original.result_data,
            tags=original.tags or [],
        )
        return await self.repo.create(copy)

    async def toggle_favorite(self, result_id: int, user_id: int) -> bool | None:
        item = await self.repo.get_by_user(result_id, user_id)
        if item is None:
            return None
        new_value = not item.is_favorite
        await self.repo.update_favorite(result_id, user_id, new_value)
        return new_value

    async def update_tags(self, result_id: int, user_id: int, tags: list[str]) -> bool:
        return await self.repo.update_tags(result_id, user_id, tags)
