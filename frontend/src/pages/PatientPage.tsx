import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Building2,
  CalendarDays,
  MapPin,
  Stethoscope,
  Wallet,
} from "lucide-react";
import { Card, CardHeader } from "@/components/ui/Card";
import { StatCard } from "@/components/ui/StatCard";
import { CardSkeleton, ChartSkeleton } from "@/components/ui/Skeleton";
import { PlotlyChart } from "@/components/PlotlyChart";
import { AISummaryCard } from "@/components/patient/AISummaryCard";
import { Timeline } from "@/components/patient/Timeline";
import { RecordsTable } from "@/components/patient/RecordsTable";
import { ExportMenu } from "@/components/patient/ExportMenu";
import {
  getClaimsPerHospital,
  getClaimsPerYear,
  getPatientCities,
  getPatientDiseases,
  getPatientDoctors,
  getPatientHospitals,
  getPatientStats,
  getVisitsPerMonth,
} from "@/lib/api";

const TABS = ["Overview", "Analytics", "Timeline", "Records"] as const;
type Tab = (typeof TABS)[number];

export function PatientPage() {
  const { name = "" } = useParams();
  const [tab, setTab] = useState<Tab>("Overview");

  const { data: stats, isLoading: statsLoading, isError } = useQuery({
    queryKey: ["stats", name],
    queryFn: () => getPatientStats(name),
  });

  if (isError) {
    return (
      <div className="text-center py-24">
        <p className="font-display text-2xl mb-2">No records found</p>
        <p className="text-slate-400 mb-6">We couldn't find any records for "{name}".</p>
        <Link to="/" className="text-clinical-400 hover:underline text-sm">
          ← Back to search
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <Link to="/" className="no-print flex items-center gap-1.5 text-sm text-slate-400 hover:text-clinical-400 transition-colors mb-2">
            <ArrowLeft size={14} /> Back to search
          </Link>
          <h1 className="font-display text-2xl md:text-3xl font-medium tracking-tight">
            {statsLoading ? "Loading…" : stats?.patient_name}
          </h1>
        </div>
        <ExportMenu patientName={name} />
      </div>

      {/* Tabs */}
      <div className="no-print flex gap-1 border-b border-white/10 overflow-x-auto">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2.5 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
              tab === t ? "border-clinical-400 text-clinical-300" : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "Overview" && <OverviewTab name={name} stats={stats} loading={statsLoading} />}
      {tab === "Analytics" && <AnalyticsTab name={name} />}
      {tab === "Timeline" && <Timeline patientName={name} />}
      {tab === "Records" && <RecordsTable patientName={name} />}
    </div>
  );
}

function OverviewTab({ name, stats, loading }: { name: string; stats: any; loading: boolean }) {
  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
    );
  }
  if (!stats) return null;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Total Records" value={stats.total_records} delay={0} />
        <StatCard label="Total Visits" value={stats.total_visits} delay={0.03} />
        <StatCard label="First Visit" value={stats.first_visit || "—"} accent="slate" delay={0.06} />
        <StatCard label="Last Visit" value={stats.last_visit || "—"} accent="slate" delay={0.09} />
        <StatCard label="Average Claim" value={stats.average_claim != null ? `Rs ${stats.average_claim.toLocaleString()}` : "—"} accent="amber" delay={0.12} />
        <StatCard label="Highest Claim" value={stats.highest_claim != null ? `Rs ${stats.highest_claim.toLocaleString()}` : "—"} accent="amber" delay={0.15} />
        <StatCard label="Lowest Claim" value={stats.lowest_claim != null ? `Rs ${stats.lowest_claim.toLocaleString()}` : "—"} accent="amber" delay={0.18} />
        <StatCard label="Total Claimed" value={stats.total_claimed_amount != null ? `Rs ${stats.total_claimed_amount.toLocaleString()}` : "—"} accent="amber" delay={0.21} />
      </div>

      <div className="grid md:grid-cols-3 gap-5">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
          <Card>
            <CardHeader title="Hospitals Visited" action={<Building2 size={16} className="text-clinical-400" />} />
            <ul className="space-y-1.5 text-sm text-slate-300">
              {stats.hospitals_visited.map((h: string) => (
                <li key={h} className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-clinical-400" /> {h}
                </li>
              ))}
              {stats.hospitals_visited.length === 0 && <li className="text-slate-500">No data</li>}
            </ul>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.15 }}>
          <Card>
            <CardHeader title="Doctors Consulted" action={<Stethoscope size={16} className="text-clinical-400" />} />
            <ul className="space-y-1.5 text-sm text-slate-300">
              {stats.doctors_consulted.map((d: string) => (
                <li key={d} className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-clinical-400" /> {d}
                </li>
              ))}
              {stats.doctors_consulted.length === 0 && <li className="text-slate-500">No data</li>}
            </ul>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          <Card>
            <CardHeader title="Cities Visited" action={<MapPin size={16} className="text-clinical-400" />} />
            <ul className="space-y-1.5 text-sm text-slate-300">
              {stats.cities_visited.map((c: string) => (
                <li key={c} className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-clinical-400" /> {c}
                </li>
              ))}
              {stats.cities_visited.length === 0 && <li className="text-slate-500">No data</li>}
            </ul>
          </Card>
        </motion.div>
      </div>

      <AISummaryCard patientName={name} />
    </div>
  );
}

function AnalyticsTab({ name }: { name: string }) {
  const { data: hospitals, isLoading: l1 } = useQuery({ queryKey: ["hospitals", name], queryFn: () => getPatientHospitals(name) });
  const { data: diseases, isLoading: l2 } = useQuery({ queryKey: ["diseases", name], queryFn: () => getPatientDiseases(name) });
  const { data: doctors, isLoading: l3 } = useQuery({ queryKey: ["doctors", name], queryFn: () => getPatientDoctors(name) });
  const { data: cities, isLoading: l4 } = useQuery({ queryKey: ["cities", name], queryFn: () => getPatientCities(name) });
  const { data: visitsPerMonth, isLoading: l5 } = useQuery({ queryKey: ["vpm", name], queryFn: () => getVisitsPerMonth(name) });
  const { data: claimsPerYear, isLoading: l6 } = useQuery({ queryKey: ["cpy", name], queryFn: () => getClaimsPerYear(name) });
  const { data: claimsPerHospital, isLoading: l7 } = useQuery({ queryKey: ["cph", name], queryFn: () => getClaimsPerHospital(name) });

  const loading = l1 || l2 || l3 || l4 || l5 || l6 || l7;
  if (loading) {
    return (
      <div className="grid md:grid-cols-2 gap-5">
        {Array.from({ length: 6 }).map((_, i) => (
          <ChartSkeleton key={i} />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {diseases && diseases.recurring_diseases.length > 0 && (
        <Card className="border-amber-500/20">
          <p className="text-sm text-amber-300 flex items-center gap-2">
            <CalendarDays size={15} />
            Recurring conditions detected: <strong>{diseases.recurring_diseases.join(", ")}</strong>
          </p>
        </Card>
      )}

      <div className="grid md:grid-cols-2 gap-5">
        <Card>
          <CardHeader title="Disease Frequency" subtitle="Every diagnosis across all visits" />
          <PlotlyChart
            data={[
              {
                type: "bar",
                orientation: "h",
                y: (diseases?.frequencies || []).slice(0, 10).map((d) => d.label).reverse(),
                x: (diseases?.frequencies || []).slice(0, 10).map((d) => d.count).reverse(),
                marker: { color: "#3EC3B7" },
              },
            ]}
            height={300}
          />
        </Card>

        <Card>
          <CardHeader title="Disease Share" subtitle="Proportional breakdown" />
          <PlotlyChart
            data={[
              {
                type: "pie",
                labels: (diseases?.frequencies || []).map((d) => d.label),
                values: (diseases?.frequencies || []).map((d) => d.count),
                hole: 0.5,
                textinfo: "percent",
                marker: { line: { color: "#0F1520", width: 2 } },
              },
            ]}
            height={300}
          />
        </Card>

        <Card>
          <CardHeader title="Hospital Visits" subtitle="Visit count per hospital" />
          <PlotlyChart
            data={[
              {
                type: "bar",
                x: (hospitals || []).map((h) => h.label),
                y: (hospitals || []).map((h) => h.count),
                marker: { color: "#F5A623" },
              },
            ]}
            height={280}
          />
        </Card>

        <Card>
          <CardHeader title="Doctor Frequency" subtitle="Visits per doctor" />
          <PlotlyChart
            data={[
              {
                type: "bar",
                x: (doctors || []).map((d) => d.label),
                y: (doctors || []).map((d) => d.count),
                marker: { color: "#6FDBD1" },
              },
            ]}
            height={280}
          />
        </Card>

        <Card>
          <CardHeader title="City Distribution" subtitle="Visits by city" />
          <PlotlyChart
            data={[
              {
                type: "pie",
                labels: (cities || []).map((c) => c.label),
                values: (cities || []).map((c) => c.count),
                hole: 0.5,
                textinfo: "percent",
              },
            ]}
            height={280}
          />
        </Card>

        <Card>
          <CardHeader title="Visits Per Month" subtitle="Visit frequency trend" />
          <PlotlyChart
            data={[
              {
                type: "scatter",
                mode: "lines+markers",
                x: (visitsPerMonth || []).map((v) => v.period),
                y: (visitsPerMonth || []).map((v) => v.count),
                line: { color: "#3EC3B7", shape: "spline" },
                fill: "tozeroy",
                fillcolor: "rgba(62,195,183,0.12)",
              },
            ]}
            height={280}
          />
        </Card>

        <Card>
          <CardHeader title="Claim Trend Per Year" subtitle="Total claimed amount by year" />
          <PlotlyChart
            data={[
              {
                type: "bar",
                x: (claimsPerYear || []).map((c) => c.period),
                y: (claimsPerYear || []).map((c) => c.total_claim),
                marker: { color: "#F5A623" },
              },
            ]}
            height={280}
          />
        </Card>

        <Card>
          <CardHeader title="Claims Per Hospital" subtitle="Total claimed amount by hospital" />
          <PlotlyChart
            data={[
              {
                type: "bar",
                orientation: "h",
                y: (claimsPerHospital || []).map((c) => c.hospital).reverse(),
                x: (claimsPerHospital || []).map((c) => c.total_claim).reverse(),
                marker: { color: "#1FA89C" },
              },
            ]}
            height={280}
          />
        </Card>
      </div>
    </div>
  );
}
