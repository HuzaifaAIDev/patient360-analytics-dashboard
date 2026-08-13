import { useEffect, useRef } from "react";
import Plot from "react-plotly.js";
import { useTheme } from "@/hooks/useTheme";

interface PlotlyChartProps {
  data: Plotly.Data[];
  title?: string;
  height?: number;
  layoutExtra?: Partial<Plotly.Layout>;
}

export function PlotlyChart({ data, title, height = 300, layoutExtra = {} }: PlotlyChartProps) {
  const { theme } = useTheme();
  const isDark = theme === "dark";
  const gridColor = isDark ? "rgba(255,255,255,0.06)" : "rgba(15,23,42,0.06)";
  const fontColor = isDark ? "#CBD5E1" : "#334155";
  const containerRef = useRef<HTMLDivElement>(null);

  // Ensure charts are fully, correctly rendered before the browser paints the
  // print/PDF output: Plotly's responsive sizing is driven by a `resize`
  // event, which doesn't fire automatically when print layout kicks in.
  // Forcing one right before printing (and again right after, to restore the
  // on-screen size) guarantees the exported chart matches the dashboard with
  // no clipped legends/labels and no partially-rendered frames.
  useEffect(() => {
    const forceResize = () => window.dispatchEvent(new Event("resize"));

    const mediaQueryList = window.matchMedia ? window.matchMedia("print") : null;
    const handleMediaChange = () => forceResize();

    window.addEventListener("beforeprint", forceResize);
    window.addEventListener("afterprint", forceResize);
    mediaQueryList?.addEventListener?.("change", handleMediaChange);

    return () => {
      window.removeEventListener("beforeprint", forceResize);
      window.removeEventListener("afterprint", forceResize);
      mediaQueryList?.removeEventListener?.("change", handleMediaChange);
    };
  }, []);

  return (
    <div ref={containerRef} className="avoid-break">
      <Plot
        data={data}
        layout={{
          title: title ? { text: title, font: { size: 13, color: fontColor } } : undefined,
          autosize: true,
          height,
          margin: { t: title ? 36 : 12, r: 16, l: 44, b: 40 },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          font: { family: "Manrope, sans-serif", color: fontColor, size: 11 },
          xaxis: { gridcolor: gridColor, zerolinecolor: gridColor, automargin: true },
          yaxis: { gridcolor: gridColor, zerolinecolor: gridColor, automargin: true },
          legend: { font: { color: fontColor, size: 10 }, orientation: "h", y: -0.2 },
          colorway: ["#3EC3B7", "#F5A623", "#6FDBD1", "#E8940E", "#1FA89C", "#A7EBE4"],
          ...layoutExtra,
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: "100%", height: `${height}px` }}
        useResizeHandler
      />
    </div>
  );
}
