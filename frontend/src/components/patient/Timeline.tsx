import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { ArrowDownWideNarrow, ArrowUpWideNarrow, Building2, CalendarDays, Stethoscope, Wallet } from "lucide-react";
import { Card, CardHeader } from "@/components/ui/Card";
import { getPatientTimeline } from "@/lib/api";

export function Timeline({ patientName }: { patientName: string }) {
  const [order, setOrder] = useState<"asc" | "desc">("desc");
  const { data: visits = [], isLoading } = useQuery({
    queryKey: ["timeline", patientName, order],
    queryFn: () => getPatientTimeline(patientName, order),
  });

  return (
    <Card>
      <CardHeader
        title="Visit Timeline"
        subtitle={`${visits.length} visit${visits.length === 1 ? "" : "s"} recorded`}
        action={
          <button
            onClick={() => setOrder((o) => (o === "desc" ? "asc" : "desc"))}
            className="no-print flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg border border-white/10 hover:bg-white/5 transition-colors text-slate-300"
          >
            {order === "desc" ? <ArrowDownWideNarrow size={13} /> : <ArrowUpWideNarrow size={13} />}
            {order === "desc" ? "Newest first" : "Oldest first"}
          </button>
        }
      />

      {isLoading ? (
        <p className="text-sm text-slate-400">Loading timeline…</p>
      ) : visits.length === 0 ? (
        <p className="text-sm text-slate-400">No visit history available for this patient.</p>
      ) : (
        <div className="relative pl-5 space-y-4 max-h-[520px] overflow-y-auto pr-1">
          <div className="absolute left-[7px] top-1 bottom-1 w-px bg-white/10" />
          {visits.map((visit, idx) => (
            <motion.div
              key={visit.record_id}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: Math.min(idx * 0.02, 0.3) }}
              className="relative avoid-break"
            >
              <span className="absolute -left-5 top-1.5 w-2.5 h-2.5 rounded-full bg-clinical-400 ring-4 ring-clinical-500/15" />
              <div className="rounded-xl border border-white/5 bg-white/5 p-4">
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400 mb-2">
                  <span className="flex items-center gap-1.5">
                    <CalendarDays size={13} /> {visit.visit_date || "Unknown date"}
                  </span>
                  {visit.hospital && (
                    <span className="flex items-center gap-1.5">
                      <Building2 size={13} /> {visit.hospital}
                    </span>
                  )}
                  {visit.doctor && (
                    <span className="flex items-center gap-1.5">
                      <Stethoscope size={13} /> {visit.doctor}
                    </span>
                  )}
                  {visit.claim_amount != null && (
                    <span className="flex items-center gap-1.5 data-num">
                      <Wallet size={13} /> Rs {visit.claim_amount.toLocaleString()}
                    </span>
                  )}
                </div>
                {visit.diseases.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mb-1.5">
                    {visit.diseases.map((d) => (
                      <span
                        key={d}
                        className="text-xs px-2 py-0.5 rounded-full bg-clinical-500/15 text-clinical-300 border border-clinical-500/20"
                      >
                        {d}
                      </span>
                    ))}
                  </div>
                )}
                {visit.notes && <p className="text-sm text-slate-400 italic">{visit.notes}</p>}
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </Card>
  );
}
