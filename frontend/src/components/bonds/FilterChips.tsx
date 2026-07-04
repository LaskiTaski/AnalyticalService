import { useEffect, useRef, useState } from "react";
import { ChevronDown, RotateCcw } from "lucide-react";
import { RangePair } from "../common/ui";
import { TYPE_META } from "../../lib/utils";
import type { AccentStyle, Tokens } from "../../lib/theme";
import { ALL_TYPES, type ScreenerState } from "../../hooks/useFilters";

interface Props {
  state: ScreenerState;
  update: (patch: Partial<ScreenerState>) => void;
  reset: () => void;
  activeCount: number;
  t: Tokens;
  A: AccentStyle;
}

/** Оттенки чипсов: у каждой категории фильтра свой цвет (как в референсе). */
const HUES: Record<string, { on: string; dot: string }> = {
  yield: { on: "bg-[#e21b5a] border-[#e21b5a] text-white", dot: "#ff5c8f" },
  coupon: { on: "bg-[#8a8420] border-[#8a8420] text-white", dot: "#d6cf4a" },
  days: { on: "bg-[#7c5ce8] border-[#7c5ce8] text-white", dot: "#a78dff" },
  type: { on: "bg-[#17b597] border-[#17b597] text-[#04231b]", dot: "#45dcb1" },
  listing: { on: "bg-[#2e7fd0] border-[#2e7fd0] text-white", dot: "#7db8f0" },
  risk: { on: "bg-[#d33a3a] border-[#d33a3a] text-white", dot: "#ff8080" },
};

/** Краткое резюме активного фильтра на чипе: «от 20», «12–24» и т.д. */
const rangeSummary = (min: string, max: string): string | null => {
  if (min && max) return `${min}–${max}`;
  if (min) return `от ${min}`;
  if (max) return `до ${max}`;
  return null;
};

function Chip({ id, label, summary, active, open, onToggle, children, popRef }: {
  id: string; label: string; summary: string | null; active: boolean; open: boolean;
  onToggle: () => void; children: React.ReactNode; popRef: (el: HTMLDivElement | null) => void;
}) {
  const hue = HUES[id];
  return (
    <div className="relative" ref={popRef}>
      <button onClick={onToggle} aria-expanded={open}
        className={`flex h-9 items-center gap-1.5 rounded-full border px-4 text-sm font-medium transition-colors ${
          active ? hue.on : "border-white/25 text-white/85 hover:border-white/60 hover:text-white"}`}>
        {label}
        {summary && <span className="font-semibold">· {summary}</span>}
        <ChevronDown size={13} className={`transition-transform ${open ? "rotate-180" : ""}`} />
      </button>
      {open && (
        <div className="chip-pop absolute left-0 top-11 z-30 w-64 rounded-2xl border border-[#242d28] bg-[#111513] p-3.5 text-zinc-100 shadow-2xl shadow-black/50">
          {children}
        </div>
      )}
    </div>
  );
}

export function FilterChips({ state, update, reset, activeCount, t, A }: Props) {
  const [open, setOpen] = useState<string | null>(null);
  const refs = useRef<Record<string, HTMLDivElement | null>>({});

  // Закрытие попапа: клик мимо или Escape
  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      const el = refs.current[open];
      if (el && !el.contains(e.target as Node)) setOpen(null);
    };
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(null);
    window.addEventListener("mousedown", onDown);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("mousedown", onDown);
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const toggle = (id: string) => setOpen((v) => (v === id ? null : id));
  const bind = (id: string) => (el: HTMLDivElement | null) => { refs.current[id] = el; };

  const typesOff = ALL_TYPES.filter((k) => !state.types[k]).length;
  const popLabel = "mb-2 text-[11px] font-semibold uppercase tracking-wider text-[#63706a]";

  return (
    <div className="flex flex-wrap items-center gap-2">
      <Chip id="yield" label="Доходность" popRef={bind("yield")}
        summary={rangeSummary(state.yieldMin, state.yieldMax)}
        active={!!(state.yieldMin || state.yieldMax)} open={open === "yield"} onToggle={() => toggle("yield")}>
        <div className={popLabel}>Доходность к погашению, %</div>
        <RangePair t={t} A={A} minVal={state.yieldMin} maxVal={state.yieldMax}
          onMin={(v) => update({ yieldMin: v })} onMax={(v) => update({ yieldMax: v })} />
      </Chip>

      <Chip id="coupon" label="Купон" popRef={bind("coupon")}
        summary={rangeSummary(state.couponMin, state.couponMax)}
        active={!!(state.couponMin || state.couponMax)} open={open === "coupon"} onToggle={() => toggle("coupon")}>
        <div className={popLabel}>Ставка купона, %</div>
        <RangePair t={t} A={A} minVal={state.couponMin} maxVal={state.couponMax}
          onMin={(v) => update({ couponMin: v })} onMax={(v) => update({ couponMax: v })} />
      </Chip>

      <Chip id="days" label="Срок" popRef={bind("days")}
        summary={rangeSummary(state.daysMin, state.daysMax)}
        active={!!(state.daysMin || state.daysMax)} open={open === "days"} onToggle={() => toggle("days")}>
        <div className={popLabel}>Дней до погашения</div>
        <RangePair t={t} A={A} minVal={state.daysMin} maxVal={state.daysMax}
          onMin={(v) => update({ daysMin: v })} onMax={(v) => update({ daysMax: v })} />
      </Chip>

      <Chip id="type" label="Тип бумаги" popRef={bind("type")}
        summary={typesOff > 0 ? ALL_TYPES.filter((k) => state.types[k]).map((k) => TYPE_META[k].label).join(", ") : null}
        active={typesOff > 0} open={open === "type"} onToggle={() => toggle("type")}>
        <div className={popLabel}>Показывать типы</div>
        <div className="flex flex-wrap gap-1.5">
          {ALL_TYPES.map((key) => {
            const { label, Icon } = TYPE_META[key];
            return (
              <button key={key}
                onClick={() => update({ types: { ...state.types, [key]: !state.types[key] } })}
                className={`flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
                  state.types[key] ? HUES.type.on : t.chipOff}`}>
                <Icon size={12} /> {label}
              </button>
            );
          })}
        </div>
      </Chip>

      <Chip id="listing" label="Листинг" popRef={bind("listing")}
        summary={[state.listLevelMax > 0 ? `≤${state.listLevelMax}` : null, state.nonQualifiedOnly ? "неквал." : null]
          .filter(Boolean).join(", ") || null}
        active={state.listLevelMax > 0 || state.nonQualifiedOnly}
        open={open === "listing"} onToggle={() => toggle("listing")}>
        <div className={popLabel}>Уровень листинга MOEX</div>
        <div className="mb-3 flex gap-1.5">
          {[0, 1, 2, 3].map((lvl) => (
            <button key={lvl} onClick={() => update({ listLevelMax: lvl })}
              className={`flex-1 rounded-full border py-1.5 text-xs font-medium transition-colors ${
                state.listLevelMax === lvl ? HUES.listing.on : t.chipOff}`}>
              {lvl === 0 ? "Все" : `≤${lvl}`}
            </button>
          ))}
        </div>
        <label className="flex cursor-pointer select-none items-center gap-2.5">
          <input type="checkbox" checked={state.nonQualifiedOnly}
            onChange={(e) => update({ nonQualifiedOnly: e.target.checked })}
            className="h-4 w-4" style={{ accentColor: HUES.listing.dot }} />
          <span className="text-sm">Только для неквал. инвесторов</span>
        </label>
      </Chip>

      <Chip id="risk" label="Риск-сигналы" popRef={bind("risk")}
        summary={state.riskOnly ? "только с сигналами" : null}
        active={state.riskOnly} open={open === "risk"} onToggle={() => toggle("risk")}>
        <label className="flex cursor-pointer select-none items-center gap-2.5">
          <input type="checkbox" checked={state.riskOnly}
            onChange={(e) => update({ riskOnly: e.target.checked })}
            className="h-4 w-4" style={{ accentColor: HUES.risk.dot }} />
          <span className="text-sm">Только с риск-сигналами</span>
        </label>
        <p className="mt-2 text-[11px] leading-snug text-[#63706a]">
          Эмитенты с событиями: понижение листинга, техдефолт и др.
        </p>
      </Chip>

      {(activeCount > 0 || state.search) && (
        <button onClick={reset}
          className="flex h-9 items-center gap-1.5 rounded-full px-3 text-sm font-medium text-white/70 transition-colors hover:text-white">
          <RotateCcw size={13} /> Сбросить
        </button>
      )}
    </div>
  );
}
