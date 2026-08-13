import { useQuery } from "@tanstack/react-query";
import { Sparkles, Info } from "lucide-react";
import { Card, CardHeader } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { getAISummary } from "@/lib/api";

export function AISummaryCard({ patientName }: { patientName: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ["ai-summary", patientName],
    queryFn: () => getAISummary(patientName),
  });

  return (
    <Card>
      <CardHeader
        title="AI Summary"
        subtitle="Generated overview of this patient's medical history"
        action={<Sparkles size={18} className="text-clinical-400" />}
      />
      {isLoading ? (
        <div className="space-y-2">
          <Skeleton className="h-3.5 w-full" />
          <Skeleton className="h-3.5 w-11/12" />
          <Skeleton className="h-3.5 w-4/5" />
        </div>
      ) : data?.summary ? (
        <p className="text-sm leading-relaxed text-slate-300">{data.summary}</p>
      ) : (
        <div className="flex items-start gap-2.5 text-sm text-slate-400 bg-white/5 rounded-lg px-4 py-3">
          <Info size={16} className="shrink-0 mt-0.5 text-slate-500" />
          <span>{data?.message || "AI summary is currently unavailable."}</span>
        </div>
      )}
    </Card>
  );
}
