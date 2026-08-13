import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { ArrowUpDown, ChevronLeft, ChevronRight, Search } from "lucide-react";
import { Card, CardHeader } from "@/components/ui/Card";
import { getPatientRecords } from "@/lib/api";
import type { PatientRecord } from "@/types";
import { ExportMenu } from "@/components/patient/ExportMenu";

const columns: ColumnDef<PatientRecord>[] = [
  { accessorKey: "visit_date", header: "Visit Date" },
  { accessorKey: "hospital", header: "Hospital" },
  { accessorKey: "doctor", header: "Doctor" },
  { accessorKey: "city", header: "City" },
  {
    accessorKey: "diseases",
    header: "Diseases",
    cell: (info) => (info.getValue() as string[]).join(", "),
  },
  {
    accessorKey: "claim_amount",
    header: "Claim",
    cell: (info) => {
      const v = info.getValue() as number | null;
      return v != null ? `Rs ${v.toLocaleString()}` : "—";
    },
  },
  { accessorKey: "notes", header: "Notes", cell: (info) => info.getValue() || "—" },
  { accessorKey: "source_file", header: "Source File" },
];

export function RecordsTable({ patientName }: { patientName: string }) {
  const { data = [], isLoading } = useQuery({
    queryKey: ["records", patientName],
    queryFn: () => getPatientRecords(patientName),
  });
  const [globalFilter, setGlobalFilter] = useState("");
  const [sorting, setSorting] = useState<any[]>([{ id: "visit_date", desc: true }]);

  const table = useReactTable({
    data,
    columns,
    state: { globalFilter, sorting },
    onGlobalFilterChange: setGlobalFilter,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: 10 } },
  });

  return (
    <Card>
      <CardHeader
        title="Complete Record Table"
        subtitle={`${data.length} record${data.length === 1 ? "" : "s"} · every field from the source JSON`}
        action={<ExportMenu patientName={patientName} />}
      />

      <div className="relative mb-4 max-w-xs no-print">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={14} />
        <input
          value={globalFilter}
          onChange={(e) => setGlobalFilter(e.target.value)}
          placeholder="Filter records…"
          className="w-full pl-9 pr-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-clinical-500/50"
        />
      </div>

      {isLoading ? (
        <p className="text-sm text-slate-400">Loading records…</p>
      ) : (
        <>
          <div className="overflow-x-auto rounded-xl border border-white/5">
            <table className="w-full text-sm">
              <thead>
                {table.getHeaderGroups().map((hg) => (
                  <tr key={hg.id} className="border-b border-white/10 bg-white/5">
                    {hg.headers.map((header) => (
                      <th
                        key={header.id}
                        onClick={header.column.getToggleSortingHandler()}
                        className="text-left px-3.5 py-2.5 font-medium text-slate-300 cursor-pointer select-none whitespace-nowrap"
                      >
                        <span className="flex items-center gap-1.5">
                          {flexRender(header.column.columnDef.header, header.getContext())}
                          <ArrowUpDown size={11} className="text-slate-500" />
                        </span>
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody>
                {table.getRowModel().rows.map((row) => (
                  <tr key={row.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="px-3.5 py-2.5 text-slate-300 whitespace-nowrap max-w-[220px] overflow-hidden text-ellipsis">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))}
                {table.getRowModel().rows.length === 0 && (
                  <tr>
                    <td colSpan={columns.length} className="text-center py-8 text-slate-500">
                      No records match your filter.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between mt-4 text-sm text-slate-400 no-print">
            <span>
              Page {table.getState().pagination.pageIndex + 1} of {Math.max(table.getPageCount(), 1)}
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
                className="p-1.5 rounded-lg border border-white/10 disabled:opacity-30 hover:bg-white/5 transition-colors"
              >
                <ChevronLeft size={15} />
              </button>
              <button
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
                className="p-1.5 rounded-lg border border-white/10 disabled:opacity-30 hover:bg-white/5 transition-colors"
              >
                <ChevronRight size={15} />
              </button>
            </div>
          </div>
        </>
      )}
    </Card>
  );
}
