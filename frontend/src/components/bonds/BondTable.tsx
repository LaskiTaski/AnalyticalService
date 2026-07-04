import { ArrowDown, ArrowUp, ArrowUpDown, Lock } from "lucide-react";
import type { Bond } from "../../api/types";
import type { AccentStyle, Tokens } from "../../lib/theme";
import { fmt, fmtDate, fmtInt, fmtVol, typeMeta } from "../../lib/utils";
import { IssuerAvatar, ListLevelBadge } from "../common/ui";

const COLUMNS = [
  { key: "short_name", label: "Название", align: "left", sortKey: "secid" },
  { key: "prev_price", label: "Цена, %", align: "right", sortKey: "prev_price" },
  { key: "yield", label: "Доходность", align: "right", sortKey: "yield_at_prev_wa_price" },
  { key: "coupon", label: "Купон, %", align: "right", sortKey: "coupon_percent" },
  { key: "maturity", label: "Погашение", align: "right", sortKey: "days_to_maturity" },
  { key: "volume", label: "Объём, ₽", align: "right", sortKey: "volume_today" },
  { key: "list_level", label: "Листинг", align: "center", sortKey: "list_level" },
] as const;

interface Props {
  items: Bond[];
  loading: boolean;
  sortBy: string;
  sortOrder: "asc" | "desc";
  onSort: (field: string) => void;
  onOpen: (secid: string) => void;
  onReset: () => void;
  selected: string | null;
  t: Tokens;
  A: AccentStyle;
  dark: boolean;
}

/** Скелетон первой загрузки: строки-заглушки вместо пустого экрана. */
function SkeletonRows({ t }: { t: Tokens }) {
  return (
    <>
      {Array.from({ length: 12 }).map((_, i) => (
        <tr key={i} className={`border-b ${t.border} ${i % 2 ? t.rowEven : t.rowOdd}`}>
          <td className="px-4 py-3">
            <div className="flex items-center gap-3">
              <div className={`skeleton h-8 w-8 rounded-lg ${t.soft}`} />
              <div className="flex flex-col gap-1.5">
                <div className={`skeleton h-3 w-32 rounded ${t.soft}`} />
                <div className={`skeleton h-2.5 w-24 rounded ${t.soft}`} />
              </div>
            </div>
          </td>
          {COLUMNS.slice(1).map((c) => (
            <td key={c.key} className="px-4 py-3">
              <div className={`skeleton ml-auto h-3 w-14 rounded ${t.soft}`} />
            </td>
          ))}
        </tr>
      ))}
    </>
  );
}

export function BondTable({ items, loading, sortBy, sortOrder, onSort, onOpen, onReset, selected, t, A, dark }: Props) {
  const initialLoading = loading && items.length === 0;
  return (
    <table className={`w-full border-collapse text-sm transition-opacity duration-150 ${
      loading && !initialLoading ? "opacity-50" : "opacity-100"}`}>
      <thead className={`sticky top-0 z-10 border-b text-xs ${t.thead}`}>
        <tr>
          {COLUMNS.map((c) => (
            <th key={c.key} onClick={() => onSort(c.sortKey)}
              className={`cursor-pointer select-none whitespace-nowrap px-4 py-3 font-semibold uppercase tracking-wide transition-colors ${A.hover} ${
                c.align === "right" ? "text-right" : c.align === "center" ? "text-center" : "text-left"}`}>
              <span className={`inline-flex items-center gap-1 ${c.align === "right" ? "flex-row-reverse" : ""}`}>
                {c.label}
                {sortBy === c.sortKey
                  ? sortOrder === "desc"
                    ? <ArrowDown size={12} className={A.text} />
                    : <ArrowUp size={12} className={A.text} />
                  : <ArrowUpDown size={12} className="opacity-40" />}
              </span>
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {initialLoading && <SkeletonRows t={t} />}
        {items.length === 0 && !loading && (
          <tr>
            <td colSpan={COLUMNS.length} className={`px-4 py-14 text-center ${t.muted}`}>
              <p className="font-medium">Ничего не найдено</p>
              <p className={`mt-1 text-xs ${t.faint}`}>Смягчите условия или сбросьте фильтры</p>
              <button onClick={onReset} className={`mt-3 rounded-lg border px-3 py-1.5 text-xs ${t.btn}`}>
                Сбросить фильтры
              </button>
            </td>
          </tr>
        )}
        {items.map((b, i) => (
          <tr key={b.secid} onClick={() => onOpen(b.secid)}
            className={`cursor-pointer border-b transition-colors last:border-b-0 ${t.border} ${
              selected === b.secid ? A.soft : `${i % 2 ? t.rowEven : t.rowOdd} ${t.rowHover}`}`}>
            <td className="px-4 py-2.5">
              <div className="flex items-center gap-3">
                <IssuerAvatar name={b.short_name} secid={b.secid} size={32} />
                <div className="min-w-0">
                  <div className={`flex items-center gap-1.5 font-medium ${A.hover}`}>
                    <span className="truncate">{b.short_name ?? b.secid}</span>
                    {b.qualified_only && <Lock size={11} className={t.faint} />}
                    {b.risk_events_count > 0 && (
                      <span
                        title={`Риск-сигналы эмитента: ${b.risk_events_count}. Подробности — во вкладке «Эмитент»`}
                        aria-label="Есть риск-сигналы эмитента"
                        className={`inline-block h-2 w-2 shrink-0 rounded-full ${
                          b.has_severe_events ? "bg-red-500" : "bg-amber-400"}`}
                      />
                    )}
                  </div>
                  <div className={`flex items-center gap-1.5 font-mono text-[11px] ${t.faint}`}>
                    <span>{b.secid}</span>
                    <span aria-hidden="true">·</span>
                    <span>{typeMeta(b.security_type).label}</span>
                  </div>
                </div>
              </div>
            </td>
            <td className="whitespace-nowrap px-4 py-2.5 text-right tabular-nums">{fmt(b.prev_price)}</td>
            <td className={`whitespace-nowrap px-4 py-2.5 text-right font-semibold tabular-nums ${
              (b.yield_at_prev_wa_price ?? 0) >= 16 ? t.up : ""}`}>
              {b.yield_at_prev_wa_price != null ? `${fmt(b.yield_at_prev_wa_price)}%` : "—"}
            </td>
            <td className="whitespace-nowrap px-4 py-2.5 text-right tabular-nums">
              {fmt(b.coupon_percent)}
              {b.coupon_frequency != null && (
                <span className={`ml-1 text-[11px] ${t.faint}`}>×{b.coupon_frequency}</span>
              )}
            </td>
            <td className="whitespace-nowrap px-4 py-2.5 text-right tabular-nums">
              <div>{b.days_to_maturity != null ? `${fmtInt(b.days_to_maturity)} дн.` : "—"}</div>
              <div className={`text-[11px] ${t.faint}`}>{fmtDate(b.mat_date)}</div>
            </td>
            <td className={`whitespace-nowrap px-4 py-2.5 text-right tabular-nums ${t.muted}`}>
              {fmtVol(b.volume_today)}
            </td>
            <td className="px-4 py-2.5 text-center">
              <ListLevelBadge level={b.list_level} dark={dark} />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
