import { AlertCircle, RefreshCw } from "lucide-react";

interface ErrorMessageProps {
  message?: string;
  onRetry?: () => void;
}

export default function ErrorMessage({
  message = "Une erreur est survenue.",
  onRetry,
}: ErrorMessageProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="w-12 h-12 rounded-full bg-accent-red/10 flex items-center justify-center mb-4">
        <AlertCircle size={24} className="text-accent-red" />
      </div>
      <p className="text-text-primary font-medium mb-1">{message}</p>
      <p className="text-sm text-text-secondary mb-4">
        Que faire ? Vérifiez votre connexion Internet ou réessayez dans quelques
        instants.
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-2 px-4 py-2 text-sm rounded-lg bg-accent-blue/10 text-accent-blue hover:bg-accent-blue/20 transition-colors"
        >
          <RefreshCw size={16} />
          Réessayer
        </button>
      )}
    </div>
  );
}
