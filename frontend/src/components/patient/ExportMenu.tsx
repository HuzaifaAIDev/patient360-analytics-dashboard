import { useEffect, useRef, useState } from "react";
import { Download, FileSpreadsheet, FileJson, FileText, Printer, ChevronDown } from "lucide-react";
import { exportUrl } from "@/lib/api";

export function ExportMenu({ patientName }: { patientName: string }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const options = [
    { label: "Export CSV", icon: FileSpreadsheet, href: exportUrl("csv", patientName) },
    { label: "Export Excel", icon: FileSpreadsheet, href: exportUrl("excel", patientName) },
    { label: "Export JSON", icon: FileJson, href: exportUrl("json", patientName) },
    { label: "Export PDF Report", icon: FileText, href: exportUrl("pdf", patientName) },
  ];

  return (
    <div ref={ref} className="relative no-print">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-white/10 hover:bg-white/5 transition-colors text-slate-300"
      >
        <Download size={13} />
        Export
        <ChevronDown size={12} />
      </button>
      {open && (
        <div className="absolute right-0 mt-1.5 w-52 glass rounded-xl overflow-hidden shadow-glass z-20">
          {options.map((opt) => (
            <a
              key={opt.label}
              href={opt.href}
              className="flex items-center gap-2.5 px-3.5 py-2.5 text-sm hover:bg-white/5 transition-colors text-slate-300"
            >
              <opt.icon size={14} className="text-clinical-400" />
              {opt.label}
            </a>
          ))}
          <button
            onClick={() => {
              setOpen(false);
              window.print();
            }}
            className="w-full flex items-center gap-2.5 px-3.5 py-2.5 text-sm hover:bg-white/5 transition-colors text-slate-300 text-left"
          >
            <Printer size={14} className="text-clinical-400" />
            Print View
          </button>
        </div>
      )}
    </div>
  );
}
