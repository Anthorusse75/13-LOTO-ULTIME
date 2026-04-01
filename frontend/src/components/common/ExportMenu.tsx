import api from "@/services/api";
import { Download, FileJson, FileSpreadsheet, FileText } from "lucide-react";
import { useRef, useState } from "react";

interface ExportGrid {
  numbers: number[];
  stars?: number[] | null;
  total_score: number;
  method?: string | null;
}

interface ExportMenuProps {
  title?: string;
  grids: ExportGrid[];
}

const FORMATS = [
  { key: "csv", label: "CSV", icon: FileSpreadsheet, mime: "text/csv" },
  { key: "json", label: "JSON", icon: FileJson, mime: "application/json" },
  { key: "pdf", label: "PDF", icon: FileText, mime: "application/pdf" },
] as const;

export default function ExportMenu({ title = "Export Loto Ultime", grids }: ExportMenuProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const handleExport = async (format: string) => {
    setLoading(true);
    setOpen(false);
    try {
      const response = await api.post(
        `/api/v1/export/${format}`,
        { title, grids },
        { responseType: "blob" },
      );
      const blob = new Blob([response.data]);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const ext = format;
      a.download = `loto_ultime.${ext}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      // silently fail — user can retry
    } finally {
      setLoading(false);
    }
  };

  if (grids.length === 0) return null;

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((o) => !o)}
        disabled={loading}
        className="flex items-center gap-2 px-3 py-2 text-sm rounded-lg border border-border bg-surface hover:bg-surface-hover text-text-secondary transition-colors disabled:opacity-50"
      >
        <Download size={16} />
        <span className="hidden sm:inline">Exporter</span>
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-full mt-1 z-50 w-40 bg-surface border border-border rounded-lg shadow-lg py-1">
            {FORMATS.map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => handleExport(key)}
                className="flex items-center gap-3 w-full px-4 py-2 text-sm text-text-secondary hover:bg-surface-hover hover:text-text-primary transition-colors"
              >
                <Icon size={16} />
                {label}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
