import { useCallback, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import type { BondFilterParams } from "../api/types";

/**
 * Состояние скринера живёт в URL search params (см. docs/FRONTEND.md):
 * ссылкой можно делиться, работает кнопка «Назад», настройки переживают F5.
 *
 * /screener?yield_min=10&days_max=365&types=corp&sort_by=...&order=desc
 */

export interface ScreenerState {
  yieldMin: string;
  yieldMax: string;
  couponMin: string;
  couponMax: string;
  daysMin: string;
  daysMax: string;
  types: Record<"ofz" | "corp" | "muni", boolean>;
  listLevelMax: number; // 0 = все
  nonQualifiedOnly: boolean;
  riskOnly: boolean; // только бумаги эмитентов с риск-сигналами
  search: string;
  sortBy: string;
  sortOrder: "asc" | "desc";
  page: number;
  perPage: number;
}

export const ALL_TYPES = ["ofz", "corp", "muni"] as const;
export const PER_PAGE_OPTIONS = [20, 50, 100] as const;

export const DEFAULT_STATE: ScreenerState = {
  yieldMin: "", yieldMax: "", couponMin: "", couponMax: "", daysMin: "", daysMax: "",
  types: { ofz: true, corp: true, muni: true },
  listLevelMax: 0,
  nonQualifiedOnly: false,
  riskOnly: false,
  search: "",
  sortBy: "yield_at_prev_wa_price",
  sortOrder: "desc",
  page: 1,
  perPage: 20,
};

function parseState(sp: URLSearchParams): ScreenerState {
  const typesParam = sp.get("types");
  const active = typesParam ? typesParam.split(",").filter(Boolean) : [...ALL_TYPES];
  return {
    yieldMin: sp.get("yield_min") ?? "",
    yieldMax: sp.get("yield_max") ?? "",
    couponMin: sp.get("coupon_min") ?? "",
    couponMax: sp.get("coupon_max") ?? "",
    daysMin: sp.get("days_min") ?? "",
    daysMax: sp.get("days_max") ?? "",
    types: {
      ofz: active.includes("ofz"),
      corp: active.includes("corp"),
      muni: active.includes("muni"),
    },
    listLevelMax: Number(sp.get("list_level_max")) || 0,
    nonQualifiedOnly: sp.get("qualified") === "false",
    riskOnly: sp.get("risk") === "1",
    search: sp.get("search") ?? "",
    sortBy: sp.get("sort_by") ?? DEFAULT_STATE.sortBy,
    sortOrder: sp.get("order") === "asc" ? "asc" : "desc",
    page: Math.max(1, Number(sp.get("page")) || 1),
    perPage: PER_PAGE_OPTIONS.includes(Number(sp.get("per_page")) as never)
      ? Number(sp.get("per_page"))
      : DEFAULT_STATE.perPage,
  };
}

function serializeState(s: ScreenerState): URLSearchParams {
  const sp = new URLSearchParams();
  const set = (k: string, v: string) => v && sp.set(k, v);
  set("yield_min", s.yieldMin);
  set("yield_max", s.yieldMax);
  set("coupon_min", s.couponMin);
  set("coupon_max", s.couponMax);
  set("days_min", s.daysMin);
  set("days_max", s.daysMax);
  const active = ALL_TYPES.filter((t) => s.types[t]);
  if (active.length > 0 && active.length < ALL_TYPES.length) sp.set("types", active.join(","));
  if (s.listLevelMax > 0) sp.set("list_level_max", String(s.listLevelMax));
  if (s.nonQualifiedOnly) sp.set("qualified", "false");
  if (s.riskOnly) sp.set("risk", "1");
  set("search", s.search);
  if (s.sortBy !== DEFAULT_STATE.sortBy) sp.set("sort_by", s.sortBy);
  if (s.sortOrder !== DEFAULT_STATE.sortOrder) sp.set("order", s.sortOrder);
  if (s.page > 1) sp.set("page", String(s.page));
  if (s.perPage !== DEFAULT_STATE.perPage) sp.set("per_page", String(s.perPage));
  return sp;
}

export function useFilters() {
  const [searchParams, setSearchParams] = useSearchParams();
  const state = useMemo(() => parseState(searchParams), [searchParams]);

  const update = useCallback(
    (patch: Partial<ScreenerState>, resetPage = true) => {
      const next = { ...parseState(new URLSearchParams(window.location.search)), ...patch };
      if (resetPage && patch.page === undefined) next.page = 1;
      setSearchParams(serializeState(next), { replace: true });
    },
    [setSearchParams],
  );

  const reset = useCallback(() => setSearchParams(new URLSearchParams(), { replace: true }), [setSearchParams]);

  /** Активные фильтры (для бейджа на кнопке «Фильтры»). */
  const activeCount =
    [state.yieldMin, state.yieldMax, state.couponMin, state.couponMax, state.daysMin, state.daysMax]
      .filter((v) => v !== "").length +
    (ALL_TYPES.some((t) => !state.types[t]) ? 1 : 0) +
    (state.listLevelMax > 0 ? 1 : 0) +
    (state.nonQualifiedOnly ? 1 : 0) +
    (state.riskOnly ? 1 : 0);

  /** Преобразование UI-состояния в query-параметры API. */
  const apiParams: BondFilterParams = useMemo(() => {
    const num = (v: string) => (v === "" ? undefined : Number(v));
    const active = ALL_TYPES.filter((t) => state.types[t]);
    return {
      page: state.page,
      per_page: state.perPage,
      yield_min: num(state.yieldMin),
      yield_max: num(state.yieldMax),
      coupon_min: num(state.couponMin),
      coupon_max: num(state.couponMax),
      days_min: num(state.daysMin),
      days_max: num(state.daysMax),
      list_level_max: state.listLevelMax > 0 ? state.listLevelMax : undefined,
      qualified: state.nonQualifiedOnly ? false : undefined,
      risk_only: state.riskOnly || undefined,
      security_type:
        active.length > 0 && active.length < ALL_TYPES.length ? active.join(",") : undefined,
      search: state.search.trim() || undefined,
      sort_by: state.sortBy,
      sort_order: state.sortOrder,
    };
  }, [state]);

  return { state, update, reset, activeCount, apiParams };
}
