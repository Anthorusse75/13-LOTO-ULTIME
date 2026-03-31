import { useEffect, useState } from "react";
import { Timer } from "lucide-react";

interface Props {
  nextDrawDate: string | null;
}

export default function NextDrawCountdown({ nextDrawDate }: Props) {
  const [remaining, setRemaining] = useState("");

  useEffect(() => {
    if (!nextDrawDate) return;
    const target = new Date(nextDrawDate).getTime();

    function update() {
      const now = Date.now();
      const diff = target - now;
      if (diff <= 0) {
        setRemaining("Tirage imminent !");
        return;
      }
      const days = Math.floor(diff / 86_400_000);
      const hours = Math.floor((diff % 86_400_000) / 3_600_000);
      const minutes = Math.floor((diff % 3_600_000) / 60_000);
      const seconds = Math.floor((diff % 60_000) / 1_000);

      const parts: string[] = [];
      if (days > 0) parts.push(`${days}j`);
      parts.push(`${hours}h`);
      parts.push(`${String(minutes).padStart(2, "0")}m`);
      parts.push(`${String(seconds).padStart(2, "0")}s`);
      setRemaining(parts.join(" "));
    }

    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, [nextDrawDate]);

  if (!nextDrawDate) return null;

  return (
    <div className="rounded-xl border border-accent-blue/30 bg-accent-blue/5 p-4 flex items-center gap-3">
      <Timer size={20} className="text-accent-blue shrink-0" />
      <div>
        <p className="text-xs text-text-secondary">Prochain tirage</p>
        <p className="text-lg font-bold text-text-primary tracking-wide">
          {remaining}
        </p>
      </div>
    </div>
  );
}
