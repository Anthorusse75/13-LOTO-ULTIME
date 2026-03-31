import {
  useMarkAllRead,
  useMarkRead,
  useNotifications,
} from "@/hooks/useNotifications";
import type { NotificationItem } from "@/types/notification";
import { CheckCheck, Loader2 } from "lucide-react";

interface Props {
  onClose: () => void;
}

export default function NotificationDropdown({ onClose: _onClose }: Props) {
  const { data, isLoading } = useNotifications(20);
  const markRead = useMarkRead();
  const markAllRead = useMarkAllRead();

  const notifications = data?.notifications ?? [];
  const unread = data?.unread_count ?? 0;

  const handleClick = (n: NotificationItem) => {
    if (!n.is_read) {
      markRead.mutate(n.id);
    }
  };

  return (
    <div className="absolute right-0 top-full mt-2 w-80 max-h-96 overflow-hidden rounded-xl border border-surface-border bg-surface-card shadow-xl z-50 flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b border-surface-border">
        <h3 className="text-sm font-semibold text-text-primary">
          Notifications {unread > 0 && `(${unread})`}
        </h3>
        {unread > 0 && (
          <button
            onClick={() => markAllRead.mutate()}
            className="text-xs text-accent-blue hover:underline flex items-center gap-1"
          >
            <CheckCheck size={14} />
            Tout lire
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 size={18} className="animate-spin text-accent-blue" />
          </div>
        ) : notifications.length === 0 ? (
          <div className="py-8 text-center text-sm text-text-tertiary">
            Aucune notification
          </div>
        ) : (
          notifications.map((n) => (
            <button
              key={n.id}
              onClick={() => handleClick(n)}
              className={`w-full text-left px-4 py-3 border-b border-surface-border/50 hover:bg-surface-hover transition-colors ${
                !n.is_read ? "bg-accent-blue/5" : ""
              }`}
            >
              <div className="flex items-start gap-2">
                {!n.is_read && (
                  <span className="mt-1.5 w-2 h-2 rounded-full bg-accent-blue shrink-0" />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-text-primary truncate">
                    {n.title}
                  </p>
                  <p className="text-xs text-text-secondary mt-0.5 line-clamp-2">
                    {n.message}
                  </p>
                  <p className="text-[10px] text-text-tertiary mt-1">
                    {new Date(n.created_at).toLocaleString("fr-FR")}
                  </p>
                </div>
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
