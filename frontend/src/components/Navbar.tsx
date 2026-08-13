import { Link, useLocation } from "react-router-dom";
import { Activity, Database, Moon, Sun } from "lucide-react";
import { useTheme } from "@/hooks/useTheme";
import { SearchBar } from "@/components/SearchBar";

export function Navbar() {
  const { theme, toggle } = useTheme();
  const location = useLocation();
  const showInlineSearch = location.pathname !== "/";

  return (
    <header className="no-print sticky top-0 z-40 glass border-b">
      <div className="max-w-7xl mx-auto px-4 md:px-6 py-3.5 flex items-center gap-4">
        <Link to="/" className="flex items-center gap-2.5 shrink-0 group">
          <span className="w-9 h-9 rounded-xl bg-clinical-500/15 border border-clinical-500/30 flex items-center justify-center text-clinical-400 group-hover:bg-clinical-500/25 transition-colors">
            <Activity size={18} />
          </span>
          <span className="hidden sm:block">
            <span className="font-display text-[1.05rem] font-medium tracking-tight leading-none block">
              Patient 360
            </span>
            <span className="text-[0.65rem] uppercase tracking-widest text-slate-400 leading-none">
              Analytics Dashboard
            </span>
          </span>
        </Link>

        {showInlineSearch && (
          <div className="flex-1 hidden md:block max-w-md">
            <SearchBar />
          </div>
        )}

        <div className="ml-auto flex items-center gap-2">
          <Link
            to="/database"
            className="flex items-center gap-1.5 text-sm px-3 py-2 rounded-lg hover:bg-white/5 transition-colors text-slate-300"
          >
            <Database size={15} />
            <span className="hidden sm:inline">Database</span>
          </Link>
          <button
            onClick={toggle}
            aria-label="Toggle dark/light mode"
            className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-white/5 transition-colors text-slate-300"
          >
            {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </div>
      </div>
    </header>
  );
}
