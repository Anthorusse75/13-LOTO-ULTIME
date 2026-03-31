import { Inbox } from "lucide-react";

interface EmptyStateProps {
  title?: string;
  message: string;
  icon?: React.ReactNode;
}

export default function EmptyState({
  title,
  message,
  icon,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="text-text-secondary mb-3">
        {icon ?? <Inbox size={40} strokeWidth={1.5} />}
      </div>
      {title && (
        <h3 className="text-sm font-semibold text-text-primary mb-1">
          {title}
        </h3>
      )}
      <p className="text-xs text-text-secondary max-w-sm">{message}</p>
    </div>
  );
}
