import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Search, User } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { searchPatients } from "@/lib/api";

export function SearchBar({ autoFocus = false }: { autoFocus?: boolean }) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const { data: suggestions = [], isFetching } = useQuery({
    queryKey: ["search", query],
    queryFn: () => searchPatients(query, 8),
    enabled: query.trim().length > 0,
  });

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const selectPatient = (name: string) => {
    setQuery("");
    setOpen(false);
    navigate(`/patient/${encodeURIComponent(name)}`);
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (!open || suggestions.length === 0) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((i) => Math.min(i + 1, suggestions.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter" && activeIndex >= 0) {
      e.preventDefault();
      selectPatient(suggestions[activeIndex].patient_name);
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  };

  return (
    <div ref={containerRef} className="relative w-full max-w-xl">
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-slate-400" size={18} />
        <input
          autoFocus={autoFocus}
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
            setActiveIndex(-1);
          }}
          onFocus={() => query && setOpen(true)}
          onKeyDown={onKeyDown}
          placeholder="Search patient by name — try a partial or misspelled name…"
          className="w-full pl-11 pr-4 py-3.5 rounded-xl glass text-sm md:text-base placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-clinical-500/60 transition-shadow"
        />
      </div>

      <AnimatePresence>
        {open && query.trim() && (
          <motion.div
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.15 }}
            className="absolute z-30 mt-2 w-full glass rounded-xl overflow-hidden shadow-glass max-h-80 overflow-y-auto"
          >
            {isFetching && suggestions.length === 0 && (
              <div className="px-4 py-3 text-sm text-slate-400">Searching…</div>
            )}
            {!isFetching && suggestions.length === 0 && (
              <div className="px-4 py-3 text-sm text-slate-400">No matching patients found.</div>
            )}
            {suggestions.map((s, idx) => (
              <button
                key={s.patient_name}
                onClick={() => selectPatient(s.patient_name)}
                onMouseEnter={() => setActiveIndex(idx)}
                className={`w-full flex items-center justify-between gap-3 px-4 py-3 text-left transition-colors ${
                  idx === activeIndex ? "bg-clinical-500/15" : "hover:bg-white/5"
                }`}
              >
                <span className="flex items-center gap-2.5 min-w-0">
                  <User size={15} className="text-clinical-400 shrink-0" />
                  <span className="truncate">{s.patient_name}</span>
                </span>
                <span className="text-xs text-slate-400 shrink-0 data-num">
                  {s.visit_count} visit{s.visit_count === 1 ? "" : "s"} · {Math.round(s.score)}%
                </span>
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
