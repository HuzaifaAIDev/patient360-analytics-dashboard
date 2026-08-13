import { ReactNode } from "react";
import { motion } from "framer-motion";
import clsx from "clsx";

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  accent?: "teal" | "amber" | "slate";
  delay?: number;
}

const accentMap = {
  teal: "text-clinical-400",
  amber: "text-amber-400",
  slate: "text-slate-300",
};

export function StatCard({ label, value, icon, accent = "teal", delay = 0 }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay }}
      className="glass rounded-2xl p-4 md:p-5 shadow-glass avoid-break"
    >
      <div className="flex items-center justify-between">
        <p className="text-xs uppercase tracking-wider text-slate-400 font-medium">{label}</p>
        {icon && <span className={clsx("opacity-70", accentMap[accent])}>{icon}</span>}
      </div>
      <p className={clsx("data-num text-2xl md:text-[1.7rem] font-semibold mt-2", accentMap[accent])}>
        {value}
      </p>
    </motion.div>
  );
}
