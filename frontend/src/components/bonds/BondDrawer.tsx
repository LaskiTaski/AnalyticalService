import { useEffect, useRef, useState } from "react";
import { AlertTriangle, CalendarDays, ChevronRight, ExternalLink, Lock, X } from "lucide-react";
import { useBond, useSimilarBonds } from "../../hooks/useBonds";
import { useIssuer, useIssuerEvents } from "../../hooks/useIssuer";
import type { AccentStyle, Tokens } from "../../lib/theme";
import { couponSchedule, fmt, fmtDate, fmtInt, fmtVol, typeMeta } from "../../lib/utils";
import { IssuerAvatar } from "../common/ui";
import { IssuerTab } from "./IssuerTab";

interface Props {
  secid: string;
  onClose: () => void;
  onSelect: (secid: string) => void;
  t: Tokens;
  A: AccentStyle;
  dark: boolean;
}

const TABS = [
  { key: "main", label: "Основное" },
  { key: "issuer", label: "Эмитент" },
  { key: "coupons", label: "Купоны" },
  { key: "similar", label: "Похожие" },
] as const;
type Tab = (typeof TABS)[number]["key"];

export function BondDrawer({ secid, onClose, onSelect, t, A, dark }: Props) {
  const [tab, setTab] = useState<Tab>("main");
  const scrollRef = useRef<HTMLDivElement>(null);

  const { data: b, isLoading, isError } = useBond(secid);
  const { data: similar = [], isLoading: similarLoading } = useSimilarBonds(b);
  const { data: issuer } = useIssuer(b?.issuer_inn);
  const { data: issuerEvents, isLoading: eventsLoading } = useIssuerEvents(b?.issuer_inn);

  useEffect(() => {
    setTab("main");
    if (scrollRef.current) scrollRef.current.scrollTop = 0;
  }, [secid]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const meta = typeMeta(b?.security_type);
  /** Официальная страница бумаги на MOEX: котировка, стакан, точное расписание купонов. */
  const moexUrl = `https://www.moex.com/ru/issue.aspx?code=${encodeURIComponent(secid)}`;
  const schedule = b ? couponSchedule(b.mat_date, b.coupon_period) : [];
  const matTime = b?.mat_date ? new Date(b.mat_date).getTime() : 0;

  const stats = b ? [
    { label: "Цена", value: `${fmt(b.prev_price)}%`, sub: `НКД ${fmt(b.accrued_int)} ₽` },
    { label: "Доходность", value: b.yield_at_prev_wa_price != null ? `${fmt(b.yield_at_prev_wa_price)}%` : "—", accent: true, sub: "к погашению" },
    { label: "Купон", value: b.coupon_value != null ? `${fmt(b.coupon_value)} ₽` : "—",
      sub: `${fmt(b.coupon_percent)}%${b.coupon_frequency ? ` · ${b.coupon_frequency} р/год` : ""}` },
    { label: "До погашения", value: b.days_to_maturity != null ? `${fmtInt(b.days_to_maturity)} дн.` : "—", sub: fmtDate(b.mat_date) },
  ] : [];

  const mainRows: [string, string | number][] = b ? [
    ["ISIN", b.isin ?? "—"],
    ["Борд MOEX", b.board_id ?? "—"],
    ["Тип", meta.full],
    ["Номинал", b.face_value != null ? `${fmt(b.face_value, 0)} ₽` : "—"],
    ["Размер лота", b.lot_size != null ? `${b.lot_size} шт.` : "—"],
    ["НКД", b.accrued_int != null ? `${fmt(b.accrued_int)} ₽` : "—"],
    ["Дюрация", b.duration != null ? `${fmtInt(Math.round(b.duration))} дн.` : "—"],
    ["Дата оферты", fmtDate(b.offer_date)],
    ["Уровень листинга", b.list_level ?? "—"],
    ["Доступ", b.qualified_only ? "Только квалифицированные" : "Все инвесторы"],
    ["Объём торгов за день", b.volume_today != null ? `${fmtVol(b.volume_today)} ₽` : "—"],
    ["Данные обновлены", fmtDate(b.updated_at)],
  ] : [];

  return (
    <>
      {/* Подложка только на мобильных: на десктопе контент сдвигается (см. App) и остаётся кликабельным */}
      <div className="fixed inset-0 z-30 lg:hidden" style={{ background: "rgba(0,0,0,.45)" }} onClick={onClose} />
      <aside
        className={`drawer-in fixed bottom-0 right-0 top-0 z-40 flex w-full max-w-md flex-col border-l shadow-2xl lg:top-14 lg:z-20 lg:shadow-none ${t.panel}`}
        role="dialog" aria-label={`Облигация ${b?.short_name ?? secid}`}>
        {/* Шапка */}
        <div className={`flex items-start justify-between gap-3 border-b p-4 ${t.border}`}>
          <div className="flex min-w-0 items-center gap-3">
            <IssuerAvatar name={b?.short_name} secid={secid} size={40} className="rounded-xl" />
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <h2 className="truncate text-base font-bold tracking-tight">{b?.short_name ?? secid}</h2>
                {b && <span className={`shrink-0 rounded-full px-2 py-0.5 text-[11px] font-medium ${A.soft}`}>{meta.label}</span>}
                {b?.qualified_only && (
                  <span className={`flex shrink-0 items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium ${
                    dark ? "bg-amber-950 text-amber-400" : "bg-amber-100 text-amber-700"}`}>
                    <Lock size={9} /> квал.
                  </span>
                )}
              </div>
              <div className={`font-mono text-[11px] ${t.faint}`}>{secid}</div>
            </div>
          </div>
          <div className="flex shrink-0 items-center gap-1.5">
            <a href={moexUrl} target="_blank" rel="noopener noreferrer"
              title="Котировка на MOEX" aria-label="Открыть страницу бумаги на MOEX"
              className={`flex h-8 w-8 items-center justify-center rounded-lg border transition-colors ${t.btn}`}>
              <ExternalLink size={14} />
            </a>
            <button onClick={onClose} aria-label="Закрыть панель"
              className={`flex h-8 w-8 items-center justify-center rounded-lg border transition-colors ${t.btn}`}>
              <X size={15} />
            </button>
          </div>
        </div>

        {/* Табы */}
        <div className={`flex gap-1 border-b px-4 ${t.border}`}>
          {TABS.map(({ key, label }) => (
            <button key={key} onClick={() => setTab(key)}
              className={`-mb-px flex items-center gap-1 border-b-2 px-3 py-2 text-sm font-medium transition-colors ${
                tab === key ? `${A.border} ${A.text}` : `border-transparent ${t.muted} ${A.hover}`}`}>
              {label}
              {key === "issuer" && (b?.risk_events_count ?? 0) > 0 && (
                <span className={`inline-block h-1.5 w-1.5 rounded-full ${
                  b?.has_severe_events ? "bg-red-500" : "bg-amber-400"}`} />
              )}
            </button>
          ))}
        </div>

        {/* Содержимое */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-4">
          {isLoading && <p className={`py-10 text-center text-sm ${t.muted}`}>Загрузка…</p>}
          {isError && (
            <p className={`py-10 text-center text-sm ${t.muted}`}>
              Не удалось загрузить данные. Проверьте, что бумага {secid} существует.
            </p>
          )}

          {b && (
            <>
              {b.has_severe_events && (
                <button onClick={() => setTab("issuer")}
                  className={`mb-3 flex w-full items-center gap-2 rounded-xl border px-3 py-2 text-left text-sm font-medium ${
                    dark ? "border-red-900 bg-red-950 text-red-300" : "border-red-200 bg-red-50 text-red-700"}`}>
                  <AlertTriangle size={15} className="shrink-0" />
                  У эмитента тяжёлые риск-события — смотрите вкладку «Эмитент»
                </button>
              )}
              <div className="mb-4 grid grid-cols-2 gap-2">
                {stats.map((s) => (
                  <div key={s.label} className={`rounded-xl border p-3 ${t.card}`}>
                    <div className={`text-[11px] ${t.faint}`}>{s.label}</div>
                    <div className={`mt-0.5 text-lg font-bold tabular-nums ${s.accent ? A.text : ""}`}>{s.value}</div>
                    {s.sub && <div className={`text-[11px] ${t.muted}`}>{s.sub}</div>}
                  </div>
                ))}
              </div>

              <a href={moexUrl} target="_blank" rel="noopener noreferrer"
                className={`mb-4 flex items-center justify-center gap-1.5 rounded-xl border py-2 text-sm font-medium transition-colors ${t.btn}`}>
                Котировка и стакан на MOEX <ExternalLink size={13} />
              </a>

              {tab === "main" && (
                <div className={`overflow-hidden rounded-xl border ${t.card}`}>
                  {mainRows.map(([k, v], i) => (
                    <div key={k}
                      className={`flex items-baseline justify-between gap-4 px-3.5 py-2.5 ${
                        i < mainRows.length - 1 ? `border-b ${t.border}` : ""}`}>
                      <span className={`text-sm ${t.muted}`}>{k}</span>
                      <span className="text-right text-sm font-medium tabular-nums">{v}</span>
                    </div>
                  ))}
                </div>
              )}

              {tab === "issuer" && (
                <IssuerTab bond={b} issuer={issuer} events={issuerEvents?.items ?? []}
                  loading={eventsLoading} t={t} A={A} dark={dark} />
              )}

              {tab === "coupons" && (
                <div className={`overflow-hidden rounded-xl border ${t.card}`}>
                  <div className={`flex items-center gap-2 border-b px-3.5 py-2.5 text-sm font-semibold ${t.border}`}>
                    <CalendarDays size={14} className={A.text} /> Ближайшие выплаты
                  </div>
                  {schedule.length === 0 && (
                    <p className={`px-3.5 py-6 text-center text-sm ${t.muted}`}>Нет данных о купонном расписании</p>
                  )}
                  {schedule.map((d, i) => {
                    const isLast = i === schedule.length - 1 && d.getTime() === matTime;
                    const amount = isLast ? (b.coupon_value ?? 0) + (b.face_value ?? 0) : b.coupon_value;
                    return (
                      <div key={i}
                        className={`flex items-center justify-between gap-2 px-3.5 py-2.5 text-sm ${i % 2 ? t.rowEven : t.rowOdd}`}>
                        <span className="tabular-nums">{fmtDate(d.toISOString())}</span>
                        <span className={`min-w-0 truncate text-[11px] ${t.faint}`}>
                          {isLast ? "купон + номинал" : `купон №${i + 1}`}
                        </span>
                        <span className="font-semibold tabular-nums">{fmt(amount)} ₽</span>
                      </div>
                    );
                  })}
                  <p className={`px-3.5 py-2 text-[11px] ${t.faint}`}>
                    Даты рассчитаны по периоду купона; точное расписание —{" "}
                    <a href={moexUrl} target="_blank" rel="noopener noreferrer"
                      className={`underline underline-offset-2 ${A.text}`}>
                      на странице бумаги MOEX
                    </a>.
                  </p>
                </div>
              )}

              {tab === "similar" && (
                <div className={`overflow-hidden rounded-xl border ${t.card}`}>
                  {similarLoading && <p className={`px-3.5 py-6 text-center text-sm ${t.muted}`}>Подбираем…</p>}
                  {!similarLoading && similar.length === 0 && (
                    <p className={`px-3.5 py-6 text-center text-sm ${t.muted}`}>Похожих бумаг не нашлось</p>
                  )}
                  {similar.map((s, i) => (
                    <button key={s.secid} onClick={() => onSelect(s.secid)}
                      className={`flex w-full items-center justify-between gap-3 px-3.5 py-2.5 text-left text-sm transition-colors ${
                        i % 2 ? t.rowEven : t.rowOdd} ${t.rowHover}`}>
                      <div className="min-w-0">
                        <div className="truncate font-medium">{s.short_name ?? s.secid}</div>
                        <div className={`font-mono text-[10px] ${t.faint}`}>{s.secid}</div>
                      </div>
                      <div className="flex shrink-0 items-center gap-3 tabular-nums">
                        <span className={`font-semibold ${t.up}`}>{fmt(s.yield_at_prev_wa_price)}%</span>
                        <span className={`text-xs ${t.faint}`}>{s.days_to_maturity ?? "—"} дн.</span>
                        <ChevronRight size={14} className={t.faint} />
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </aside>
    </>
  );
}
