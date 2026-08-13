import { Route, Routes } from "react-router-dom";
import { ThemeProvider } from "@/hooks/useTheme";
import { Navbar } from "@/components/Navbar";
import { HomePage } from "@/pages/HomePage";
import { PatientPage } from "@/pages/PatientPage";
import { DatabasePage } from "@/pages/DatabasePage";
import { NotFoundPage } from "@/pages/NotFoundPage";

export default function App() {
  return (
    <ThemeProvider>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 md:px-6 py-6 md:py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/patient/:name" element={<PatientPage />} />
            <Route path="/database" element={<DatabasePage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>
        <footer className="no-print text-center text-xs text-slate-500 py-6">
          Patient 360 Analytics Dashboard — no login, data served from a SQL database. Analytics only.
        </footer>
      </div>
    </ThemeProvider>
  );
}
