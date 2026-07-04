import { useState } from "react";
import { RotateCcw, X } from "lucide-react";
import { FilterSection, RangePair } from "../common/ui";
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
  /** Закрытие slide-over на мобильных (на десктопе кнопка скрыта). */
  onClose?: () => void;
}

export function FilterSidebar({ state, update, reset, activeCount, t, A, onClose }: Props) {
  const [sections, setSections] = useState({
    yield: true, coupon: false, days: false, type: false, listing: false, risk: false,
  });
  const toggleSec = (k: keyof typeof sections) => setSections((s) => ({ ...s, [k]: !s[k] }));

  return (
    <div className="flex h-full flex-col px-4">
      <div className={`flex items-center justify-between border-b py-3 lg:hidden ${t.border}`}>
        <span className="text-sm font-semibold">Фильтры</span>
        <button onClick={onClose} aria-label="Закрыть фильтры"
          className={`flex h-8 w-8 items-center justify-center rounded-lg border ${t.btn}`}>
          <X size={15} />
        </button>
      </div>

      <FilterSection title="Доходность, %" t={t} A={A} open={sections.yield}
        onToggle={() => toggleSec("yield")}
        badge={Number(state.yieldMin !== "") + Number(state.yieldMax !== "")}>
        <RangePair t={t} A={A} minVal={state.yieldMin} maxVal={state.yieldMax}
          onMin={(v) => update({ yieldMin: v })} onMax={(v) => update({ yieldMax: v })} />
      </FilterSection>

      <FilterSection title="Купон, %" t={t} A={A} open={sections.coupon}
        onToggle={() => toggleSec("coupon")}
        badge={Number(state.couponMin !== "") + Number(state.couponMax !== "")}>
        <RangePair t={t} A={A} minVal={state.couponMin} maxVal={state.couponMax}
          onMin={(v) => update({ couponMin: v })} onMax={(v) => update({ couponMax: v })} />
      </FilterSection>

      <FilterSection title="Срок, дней" t={t} A={A} open={sections.days}
        onToggle={() => toggleSec("days")}
        badge={Number(state.daysMin !== "") + Number(state.daysMax !== "")}>
        <RangePair t={t} A={A} minVal={state.daysMin} maxVal={state.daysMax}
          onMin={(v) => update({ daysMin: v })} onMax={(v) => update({ daysMax: v })} />
      </FilterSection>

      <FilterSection title="Тип бумаги" t={t} A={A} open={sections.type}
        onToggle={() => toggleSec("type")}
        badge={ALL_TYPES.filter((k) => !state.types[k]).length}>
        <div className="flex flex-wrap gap-1.5">
          {ALL_TYPES.map((key) => {
            const { label, Icon } = TYPE_META[key];
            return (
              <button key={key}
                onClick={() => update({ types: { ...state.types, [key]: !state.types[key] } })}
                className={`flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs font-medium transition-colors ${
                  state.types[key] ? A.chipOn : t.chipOff}`}>
                <Icon size={12} /> {label}
              </button>
            );
          })}
        </div>
      </FilterSection>

      <FilterSection title="Листинг и доступ" t={t} A={A} open={sections.listing}
        onToggle={() => toggleSec("listing")}
        badge={(state.listLevelMax > 0 ? 1 : 0) + (state.nonQualifiedOnly ? 1 : 0)}>
        <div className="mb-2 flex gap-1.5">
          {[0, 1, 2, 3].map((lvl) => (
            <button key={lvl} onClick={() => update({ listLevelMax: lvl })}
              className={`flex-1 rounded-lg border py-1.5 text-xs font-medium transition-colors ${
                state.listLevelMax === lvl ? A.chipOn : t.chipOff}`}>
              {lvl === 0 ? "Все" : `≤${lvl}`}
            </button>
          ))}
        </div>
        <label className="flex cursor-pointer items-center gap-2.5 select-none pt-1">
          <input type="checkbox" checked={state.nonQualifiedOnly}
            onChange={(e) => update({ nonQualifiedOnly: e.target.checked })}
            className="h-4 w-4" style={{ accentColor: A.hex }} />
          <span className="text-sm">Только для неквал.</span>
        </label>
      </FilterSection>

      <FilterSection title="Риск-сигналы" t={t} A={A} open={sections.risk}
        onToggle={() => toggleSec("risk")}
        badge={state.riskOnly ? 1 : 0}>
        <label className="flex cursor-pointer items-center gap-2.5 select-none pt-1">
          <input type="checkbox" checked={state.riskOnly}
            onChange={(e) => update({ riskOnly: e.target.checked })}
            className="h-4 w-4" style={{ accentColor: A.hex }} />
          <span className="text-sm">Только с риск-сигналами</span>
        </label>
        <p className={`mt-1.5 text-[11px] leading-snug ${t.faint}`}>
          Эмитенты с событиями: понижение листинга, техдефолт и др.
        </p>
      </FilterSection>

      <button onClick={reset} disabled={activeCount === 0 && !state.search}
        className={`my-3 flex w-full items-center justify-center gap-1.5 rounded-lg border py-2 text-xs font-medium transition-colors disabled:opacity-40 ${t.btn}`}>
        <RotateCcw size={12} /> Сбросить всё
      </button>
    </div>
  );
}
