import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip as RTooltip } from "recharts";
import { useBonds, useMarketOverview } from "../hooks/useBonds";
import type { Bond } from "../api/types";
import type { AccentStyle, Tokens } from "../lib/theme";
import { fmt, fmtInt, TYPE_META } from "../lib/utils";

interface Props {
  t: Tokens;
  A: AccentStyle;
  openBond: (secid: string) => void;
}

function TopList({ title, items, valueOf, loading, onOpen, t }: {
  title: string; items: Bond[]; valueOf: (b: Bond) => string;
  loading: boolean; onOpen: (secid: string) => void; t: Tokens;
}) {
  return (
    <div className={`overflow-hidden rounded-2xl border ${t.card}`}>
      <div className={`border-b px-4 py-3 text-sm font-semibold ${t.border}`}>{title}</div>
      {loading && <p className={`px-4 py-8 text-center text-sm ${t.muted}`}>Загрузка…</p>}
      {items.map((b, i) => (
        <button key={b.secid} onClick={() => onOpen(b.secid)}
          className={`flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm transition-colors ${
            i % 2 ? t.rowEven : t.rowOdd} ${t.rowHover}`}>
          <span className={`w-5 text-xs font-bold ${t.faint}`}>{i + 1}</span>
          <span className="min-w-0 flex-1 truncate font-medium">{b.short_name ?? b.secid}</span>
          <span className={`font-semibold tabular-nums ${t.up}`}>{valueOf(b)}</span>
        </button>
      ))}
    </div>
  );
}

export function DashboardPage({ t, A, openBond }: Props) {
  const { data: overview, isLoading } = useMarketOverview();
  const topYield = useBonds({ per_page: 5, sort_by: "yield_at_prev_wa_price", sort_order: "desc" });
  const topCoupon = useBonds({ per_page: 5, sort_by: "coupon_percent", sort_order: "desc" });

  const byType = Object.keys(TYPE_META)
    .map((k) => ({
      key: k,
      name: TYPE_META[k].full,
      value: overview?.by_type?.[k] ?? 0,
      hex: TYPE_META[k].hex,
    }))
    .filter((e) => e.value > 0);

  const cards = [
    { label: "Всего облигаций", value: overview ? fmtInt(overview.total_bonds) : "…" },
    { label: "Средняя доходность", value: overview?.avg_yield != null ? `${fmt(overview.avg_yield)}%` : "…", accent: true },
    { label: "Средний купон", value: overview?.avg_coupon != null ? `${fmt(overview.avg_coupon)}%` : "…" },
    { label: "Средняя дюрация", value: overview?.avg_duration != null ? `${fmtInt(Math.round(overview.avg_duration))} дн.` : "…" },
  ];

  return (
    <div className="mx-auto max-w-7xl px-4 py-5">
      <div className="mb-4 flex items-baseline justify-between">
        <h1 className="text-xl font-bold tracking-tight">Обзор рынка</h1>
        {overview?.last_updated && (
          <span className={`text-xs ${t.faint}`}>
            Данные обновлены: {new Date(overview.last_updated).toLocaleString("ru-RU")}
          </span>
        )}
      </div>
      <div className="mb-5 grid grid-cols-2 gap-3 lg:grid-cols-4">
        {cards.map((c) => (
          <div key={c.label} className={`rounded-2xl border p-4 ${t.card}`}>
            <div className={`text-xs ${t.faint}`}>{c.label}</div>
            <div className={`mt-1 text-2xl font-bold tabular-nums ${c.accent ? A.text : ""}`}>{c.value}</div>
          </div>
        ))}
      </div>
      <div className="grid gap-5 lg:grid-cols-3">
        <div className={`rounded-2xl border p-4 ${t.card}`}>
          <div className="mb-2 text-sm font-semibold">Распределение по типам</div>
          <div className="h-52">
            {isLoading ? (
              <p className={`pt-16 text-center text-sm ${t.muted}`}>Загрузка…</p>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={byType} dataKey="value" nameKey="name" innerRadius={52} outerRadius={80}
                    paddingAngle={3} strokeWidth={0}>
                    {byType.map((e) => <Cell key={e.key} fill={e.hex} />)}
                  </Pie>
                  <RTooltip contentStyle={{ background: t.tooltipBg, border: `1px solid ${t.grid}`, borderRadius: 10, fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
          <div className="mt-1 flex flex-col gap-1.5 text-sm">
            {byType.map((e) => (
              <div key={e.key} className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full" style={{ background: e.hex }} />
                <span className={`flex-1 ${t.muted}`}>{e.name}</span>
                <b className="tabular-nums">{fmtInt(e.value)}</b>
              </div>
            ))}
          </div>
        </div>
        <TopList title="Топ-5 по доходности" items={topYield.data?.items ?? []}
          valueOf={(b) => `${fmt(b.yield_at_prev_wa_price)}%`}
          loading={topYield.isLoading} onOpen={openBond} t={t} />
        <TopList title="Топ-5 по купону" items={topCoupon.data?.items ?? []}
          valueOf={(b) => `${fmt(b.coupon_percent)}%`}
          loading={topCoupon.isLoading} onOpen={openBond} t={t} />
      </div>
    </div>
  );
}
