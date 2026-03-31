import api from "./api";
import type { PaginatedResponse } from "@/types/api";
import type { SaveResultRequest, SavedResult, UpdateTagsRequest } from "@/types/history";

export const historyService = {
  save: (_gameId: number, data: SaveResultRequest) =>
    api.post<SavedResult>("/history/save", data).then((r) => r.data),

  list: (
    _gameId: number,
    page = 1,
    pageSize = 20,
    resultType?: string,
    isFavorite?: boolean,
    tag?: string,
  ) =>
    api
      .get<PaginatedResponse<SavedResult>>("/history", {
        params: {
          page,
          page_size: pageSize,
          ...(resultType && { result_type: resultType }),
          ...(isFavorite !== undefined && { is_favorite: isFavorite }),
          ...(tag && { tag }),
        },
      })
      .then((r) => r.data),

  get: (_gameId: number, id: number) =>
    api.get<SavedResult>(`/history/${id}`).then((r) => r.data),

  delete: (_gameId: number, id: number) =>
    api.delete(`/history/${id}`),

  toggleFavorite: (_gameId: number, id: number) =>
    api
      .patch<SavedResult>(`/history/${id}/favorite`)
      .then((r) => r.data),

  updateTags: (_gameId: number, id: number, data: UpdateTagsRequest) =>
    api
      .patch<SavedResult>(`/history/${id}/tags`, data)
      .then((r) => r.data),

  duplicate: (_gameId: number, id: number) =>
    api
      .post<SavedResult>(`/history/${id}/duplicate`)
      .then((r) => r.data),
};
