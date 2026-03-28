import { AlertTriangle, X } from "lucide-react";
import { useCallback, useEffect, useRef } from "react";

interface ConfirmModalProps {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: "danger" | "default";
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmModal({
  open,
  title,
  message,
  confirmLabel = "Confirmer",
  cancelLabel = "Annuler",
  variant = "default",
  onConfirm,
  onCancel,
}: ConfirmModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    else if (!open && dialog.open) dialog.close();
  }, [open]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Escape") onCancel();
    },
    [onCancel],
  );

  if (!open) return null;

  const confirmClass =
    variant === "danger"
      ? "bg-accent-red hover:bg-accent-red/80 text-white"
      : "bg-accent-blue hover:bg-accent-blue/80 text-white";

  return (
    <dialog
      ref={dialogRef}
      className="fixed inset-0 z-50 bg-transparent backdrop:bg-black/50"
      onKeyDown={handleKeyDown}
    >
      <div className="bg-surface border border-border rounded-xl shadow-lg max-w-md w-full mx-auto mt-[20vh] p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            {variant === "danger" && (
              <div className="w-10 h-10 rounded-full bg-accent-red/10 flex items-center justify-center">
                <AlertTriangle size={20} className="text-accent-red" />
              </div>
            )}
            <h2 className="text-lg font-semibold text-text-primary">{title}</h2>
          </div>
          <button
            onClick={onCancel}
            className="p-1 rounded hover:bg-surface-hover text-text-secondary"
            aria-label="Fermer"
          >
            <X size={18} />
          </button>
        </div>
        <p className="text-sm text-text-secondary mb-6">{message}</p>
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm rounded-lg border border-border text-text-secondary hover:bg-surface-hover transition-colors"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            className={`px-4 py-2 text-sm rounded-lg transition-colors ${confirmClass}`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </dialog>
  );
}
