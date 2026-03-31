import type {
  NotificationListResponse,
  UnreadCountResponse,
} from "@/types/notification";
import api from "./api";

export const notificationService = {
  list: async (
    limit = 50,
    offset = 0,
    unreadOnly = false,
  ): Promise<NotificationListResponse> => {
    const { data } = await api.get("/notifications", {
      params: { limit, offset, unread_only: unreadOnly },
    });
    return data;
  },

  getUnreadCount: async (): Promise<UnreadCountResponse> => {
    const { data } = await api.get("/notifications/unread-count");
    return data;
  },

  markRead: async (id: number): Promise<void> => {
    await api.patch(`/notifications/${id}/read`);
  },

  markAllRead: async (): Promise<void> => {
    await api.post("/notifications/read-all");
  },
};
