import { Loader2 } from "lucide-react";

interface LoadingSpinnerProps {
  message?: string;
}

export default function LoadingSpinner({ message = "Chargement\u2026" }: LoadingSpinnerProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-label={message}
      className="flex flex-col items-center justify-center py-12 gap-3"
    >
      <Loader2 size={32} className="animate-spin text-accent-blue" aria-hidden="true" />
      <p className="text-sm text-text-secondary">{message}</p>
    </div>
  );
}
