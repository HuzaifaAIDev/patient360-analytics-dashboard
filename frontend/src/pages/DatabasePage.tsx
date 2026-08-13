import { useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  CheckCircle2,
  Database,
  Globe,
  RefreshCw,
  Server,
  ShieldCheck,
  Terminal,
  XCircle,
} from "lucide-react";
import { Card, CardHeader } from "@/components/ui/Card";
import { getCorsOrigins, getDatabaseStatus } from "@/lib/api";

export function DatabasePage() {
  const queryClient = useQueryClient();

  const { data: status, isLoading, dataUpdatedAt } = useQuery({
    queryKey: ["database-status"],
    queryFn: getDatabaseStatus,
    refetchInterval: 30000,
  });

  const { data: origins = [], isLoading: originsLoading } = useQuery({
    queryKey: ["cors-origins"],
    queryFn: getCorsOrigins,
    refetchInterval: 30000,
  });

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="font-display text-2xl md:text-3xl font-medium tracking-tight">Database Connection</h1>
        <p className="text-slate-400 mt-1.5 text-sm md:text-base">
          This dashboard reads every patient record directly from a SQL database, configured entirely
          through the backend's environment file. There is no JSON upload step in this application.
        </p>
      </div>

      <Card>
        <CardHeader
          title="Live Connection Status"
          subtitle={dataUpdatedAt ? `Last checked ${new Date(dataUpdatedAt).toLocaleTimeString()}` : undefined}
          action={
            <button
              onClick={() => queryClient.invalidateQueries({ queryKey: ["database-status"] })}
              className="flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg border border-white/10 hover:bg-white/5 transition-colors text-slate-300"
            >
              <RefreshCw size={13} className={isLoading ? "animate-spin" : ""} />
              Refresh
            </button>
          }
        />

        {isLoading ? (
          <p className="text-sm text-slate-400">Checking connection…</p>
        ) : status ? (
          <div className="space-y-4">
            <div
              className={`flex items-center gap-3 rounded-xl px-4 py-3 border ${
                status.connected
                  ? "bg-clinical-500/10 border-clinical-500/25 text-clinical-300"
                  : "bg-red-500/10 border-red-500/25 text-red-300"
              }`}
            >
              {status.connected ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
              <div>
                <p className="font-medium text-sm">{status.connected ? "Connected" : "Not Connected"}</p>
                <p className="text-xs opacity-80 mt-0.5">{status.message}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <Field label="Driver" value={status.driver} icon={<Server size={14} />} />
              <Field label="Database" value={status.database_name} icon={<Database size={14} />} />
              <Field label="Host" value={status.host || "local file"} icon={<Terminal size={14} />} />
              <Field label="SSL Mode" value={status.ssl_mode || "n/a (SQLite)"} icon={<ShieldCheck size={14} />} />
            </div>

            <div className="grid grid-cols-2 gap-4 pt-1">
              <Field label="Total Records" value={String(status.total_records)} accent />
              <Field label="Unique Patients" value={String(status.unique_patients)} accent />
            </div>
          </div>
        ) : null}
      </Card>

      <Card>
        <CardHeader
          title="Allowed Origins"
          subtitle="Controlled from the database — not from a config file"
          action={<Globe size={16} className="text-clinical-400" />}
        />

        {originsLoading ? (
          <p className="text-sm text-slate-400">Loading…</p>
        ) : origins.length === 0 ? (
          <p className="text-sm text-slate-400">No origins configured yet.</p>
        ) : (
          <div className="space-y-2">
            {origins.map((o, idx) => (
              <motion.div
                key={o.origin}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: Math.min(idx * 0.03, 0.3) }}
                className="flex items-center justify-between gap-3 rounded-xl bg-white/5 border border-white/5 px-4 py-2.5"
              >
                <div className="min-w-0">
                  <p className="text-sm font-medium text-slate-200 truncate data-num">{o.origin}</p>
                  {o.note && <p className="text-xs text-slate-500 mt-0.5">{o.note}</p>}
                </div>
                <span
                  className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${
                    o.is_active
                      ? "bg-clinical-500/15 text-clinical-300 border border-clinical-500/20"
                      : "bg-white/5 text-slate-500 border border-white/10"
                  }`}
                >
                  {o.is_active ? "Active" : "Disabled"}
                </span>
              </motion.div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

function Field({
  label,
  value,
  icon,
  accent,
}: {
  label: string;
  value: string;
  icon?: React.ReactNode;
  accent?: boolean;
}) {
  return (
    <div className="rounded-xl bg-white/5 border border-white/5 p-3">
      <p className="text-[0.65rem] uppercase tracking-wider text-slate-500 flex items-center gap-1.5 mb-1">
        {icon}
        {label}
      </p>
      <p className={`text-sm font-medium truncate ${accent ? "data-num text-clinical-300" : "text-slate-200"}`}>
        {value}
      </p>
    </div>
  );
}
