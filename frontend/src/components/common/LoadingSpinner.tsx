import { Loader2 } from "lucide-react";

interface LoadingSpinnerProps {
  message?: string;
}

export default function LoadingSpinner({ message }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3">
      <Loader2 size={32} className="animate-spin text-accent-blue" />
      {message && <p className="text-sm text-text-secondary">{message}</p>}
    </div>
  );
}
