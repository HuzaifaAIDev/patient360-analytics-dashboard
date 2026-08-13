import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Building2, Stethoscope, Users, Wallet } from "lucide-react";
import { SearchBar } from "@/components/SearchBar";
import { StatCard } from "@/components/ui/StatCard";
import { Card, CardHeader } from "@/components/ui/Card";
import { PlotlyChart } from "@/components/PlotlyChart";
import { ChartSkeleton, CardSkeleton } from "@/components/ui/Skeleton";
import { getOverview, getTopPatients } from "@/lib/api";
import { useNavigate } from "react-router-dom";

function formatCurrency(n: number) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(n);
}

export function HomePage() {
  const navigate = useNavigate();
  const { data: overview, isLoading } = useQuery({ queryKey: ["overview"], queryFn: getOverview });
  const { data: topPatients = [] } = useQuery({ queryKey: ["top-patients"], queryFn: () => getTopPatients(8) });

  const isEmpty = !isLoading && overview && overview.total_records === 0;

  return (
    <div className="space-y-10 md:space-y-14">
      {/* Hero */}
      <section className="pt-6 md:pt-14 pb-4 text-center">
        <motion.p
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-xs uppercase tracking-[0.2em] text-clinical-400 font-medium mb-3"
        >
          AI-powered Patient History Analytics Platform
        </motion.p>
        <motion.h1
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="font-display text-3xl sm:text-4xl md:text-5xl font-medium tracking-tight max-w-2xl mx-auto leading-[1.15]"
        >
          Find any patient's full history in one search.
        </motion.h1>
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.12 }}
          className="mt-7 flex justify-center"
        >
          <SearchBar autoFocus />
        </motion.div>
        {isEmpty && (
          <p className="mt-4 text-sm text-slate-400">
            No data in the connected database yet.{" "}
            <button onClick={() => navigate("/database")} className="text-clinical-400 hover:underline">
              Check the database connection
            </button>{" "}
            or run the seed script to load demo data.
          </p>
        )}
      </section>

      {/* KPIs */}
      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : overview ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="Unique Patients" value={overview.unique_patients} icon={<Users size={16} />} delay={0} />
          <StatCard label="Total Records" value={overview.total_records} icon={<Stethoscope size={16} />} delay={0.05} />
          <StatCard label="Hospitals" value={overview.total_hospitals} icon={<Building2 size={16} />} delay={0.1} />
          <StatCard
            label="Total Claimed"
            value={`Rs ${formatCurrency(overview.total_claimed_amount)}`}
            icon={<Wallet size={16} />}
            accent="amber"
            delay={0.15}
          />
        </div>
      ) : null}

      {/* Charts */}
      {overview && overview.total_records > 0 && (
        <div className="grid md:grid-cols-2 gap-5">
          <Card>
            <CardHeader title="Hospital Visits" subtitle="Share of visits by hospital" />
            <PlotlyChart
              data={[
                {
                  type: "pie",
                  labels: overview.hospital_breakdown.map((h) => h.label),
                  values: overview.hospital_breakdown.map((h) => h.count),
                  hole: 0.55,
                  textinfo: "percent",
                  marker: { line: { color: "#0F1520", width: 2 } },
                },
              ]}
              height={280}
            />
          </Card>

          <Card>
            <CardHeader title="Top Diseases" subtitle="Most frequent diagnoses across all patients" />
            <PlotlyChart
              data={[
                {
                  type: "bar",
                  orientation: "h",
                  y: overview.disease_breakdown.frequencies.slice(0, 8).map((d) => d.label).reverse(),
                  x: overview.disease_breakdown.frequencies.slice(0, 8).map((d) => d.count).reverse(),
                  marker: { color: "#3EC3B7" },
                },
              ]}
              height={280}
            />
          </Card>

          <Card>
            <CardHeader title="Visits Per Month" subtitle="Volume trend across the dataset" />
            <PlotlyChart
              data={[
                {
                  type: "scatter",
                  mode: "lines+markers",
                  x: overview.visits_per_month.map((v) => v.period),
                  y: overview.visits_per_month.map((v) => v.count),
                  line: { color: "#3EC3B7", shape: "spline" },
                  fill: "tozeroy",
                  fillcolor: "rgba(62,195,183,0.12)",
                },
              ]}
              height={260}
            />
          </Card>

          <Card>
            <CardHeader title="Doctor Frequency" subtitle="Visits handled per doctor" />
            <PlotlyChart
              data={[
                {
                  type: "bar",
                  x: overview.doctor_breakdown.map((d) => d.label),
                  y: overview.doctor_breakdown.map((d) => d.count),
                  marker: { color: "#F5A623" },
                },
              ]}
              height={260}
            />
          </Card>
        </div>
      )}

      {/* Top patients */}
      {topPatients.length > 0 && (
        <Card>
          <CardHeader title="Most Frequent Patients" subtitle="By total visit count" />
          <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-3">
            {topPatients.map((p) => (
              <button
                key={p.patient_name}
                onClick={() => navigate(`/patient/${encodeURIComponent(p.patient_name)}`)}
                className="text-left rounded-xl border border-white/5 hover:border-clinical-500/40 hover:bg-white/5 transition-colors p-3.5"
              >
                <p className="font-medium truncate">{p.patient_name}</p>
                <p className="text-xs text-slate-400 mt-1 data-num">{p.visit_count} visits</p>
              </button>
            ))}
          </div>
        </Card>
      )}

      {isLoading && (
        <div className="grid md:grid-cols-2 gap-5">
          <ChartSkeleton />
          <ChartSkeleton />
        </div>
      )}
    </div>
  );
}
