import { Info } from "lucide-react";
import { useState } from "react";

interface InfoTooltipProps {
  text: string;
}

export default function InfoTooltip({ text }: InfoTooltipProps) {
  const [visible, setVisible] = useState(false);

  return (
    <span
      className="relative inline-flex items-center ml-1"
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
    >
      <Info
        size={14}
        className="text-text-secondary hover:text-accent-blue cursor-help transition-colors"
      />
      {visible && (
        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 text-xs text-text-primary bg-surface border border-border rounded-md shadow-lg whitespace-normal w-56 z-50 pointer-events-none">
          {text}
        </span>
      )}
    </span>
  );
}
