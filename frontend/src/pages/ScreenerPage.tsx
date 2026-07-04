import { useEffect, useRef, useState } from "react";
import { Search, X } from "lucide-react";
import { useBonds } from "../hooks/useBonds";
import { PER_PAGE_OPTIONS, useFilters } from "../hooks/useFilters";
import { FilterChips } from "../components/bonds/FilterChips";
import { BondTable } from "../components/bonds/BondTable";
import { Pagination } from "../components/common/ui";
import { fmt, fmtInt, plural } from "../lib/utils";
import type { AccentStyle, Tokens } from "../lib/theme";

interface Props {
  t: Tokens;
  A: AccentStyle;
  dark: boolean;
  openBond: (secid: string) => void;
  selected: string | null;
}

export function ScreenerPage({ t, A, dark, openBond, selected }: Props) {
  const { state, update, reset, activeCount, apiParams } = useFilters();

  // Поиск: локальный ввод + дебаунс перед записью в URL/запрос
  const searchRef = useRef<HTMLInputElement>(null);
  const [searchFocus, setSearchFocus] = useState(false);
  const [searchInput, setSearchInput] = useState(state.search);
  useEffect(() => setSearchInput(state.search), [state.search]);
  useEffect(() => {
    const id = setTimeout(() => {
      if (searchInput !== state.search) update({ search: searchInput });
    }, 300);
    return () => clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchInput]);

  // Хоткей «/» — фокус на поиск из любого места скринера
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const el = e.target as HTMLElement;
      if (e.key === "/" && el.tagName !== "INPUT" && el.tagName !== "TEXTAREA") {
        e.preventDefault();
        searchRef.current?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const { data, isFetching, isError, refetch } = useBonds(apiParams);

  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  const pages = Math.max(1, data?.pages ?? 1);
  const page = Math.min(state.page, pages);
  const from = total > 0 ? (page - 1) * (data?.per_page ?? state.perPage) + 1 : 0;
  const to = total > 0 ? Math.min(page * (data?.per_page ?? state.perPage), total) : 0;

  const avgYield = items.length
    ? items.reduce((s, b) => s + (b.yield_at_prev_wa_price ?? 0), 0) / items.length
    : 0;

  const toggleSort = (field: string) =>
    update(
      state.sortBy === field
        ? { sortOrder: state.sortOrder === "desc" ? "asc" : "desc" }
        : { sortBy: field, sortOrder: "desc" },
    );

  return (
    /* Всё под шапкой: герой фиксированной высоты сверху, таблица скроллится внутри */
    <div className="flex h-[calc(100dvh-3.5rem)] flex-col">
      {/* ── Герой: фирменный изумруд, заголовок, поиск, чипсы ─────────── */}
      <section className={`${t.hero} px-4 pb-5 pt-6 sm:px-6`}>
        <div className="mx-auto w-full max-w-6xl">
          <div className="flex flex-wrap items-end justify-between gap-x-6 gap-y-1">
            <h1 className={`font-display text-2xl font-extrabold tracking-tight sm:text-3xl ${t.onHero}`}>
              Найдите нужную облигацию
            </h1>
            <p className={`text-sm ${t.onHeroFaint}`}>
              <b className={`font-display text-base ${t.onHero}`}>{fmtInt(total)}</b>{" "}
              {plural(total, "бумага", "бумаги", "бумаг")} MOEX
              {items.length > 0 && (
                <> · ср. доходность на странице{" "}
                  <b className={`font-display ${t.onHero}`}>{fmt(avgYield)}%</b></>
              )}
            </p>
          </div>

          {/* Поиск: крупное скруглённое поле + круглая малиновая кнопка */}
          <div className={`relative mt-4 rounded-full border transition-shadow ${t.heroInput}`}
            style={searchFocus ? { boxShadow: `0 0 0 3px ${A.hex}55` } : undefined}>
            <input ref={searchRef} value={searchInput} onChange={(e) => setSearchInput(e.target.value)}
              onFocus={() => setSearchFocus(true)} onBlur={() => setSearchFocus(false)}
              onKeyDown={(e) => e.key === "Escape" && searchRef.current?.blur()}
              placeholder="Название, тикер или ISIN…"
              className="h-12 w-full rounded-full bg-transparent pl-5 pr-24 text-[15px] outline-none" />
            {searchInput && (
              <button onClick={() => { setSearchInput(""); update({ search: "" }); searchRef.current?.focus(); }}
                aria-label="Очистить поиск"
                className="absolute right-14 top-1/2 flex h-7 w-7 -translate-y-1/2 items-center justify-center rounded-full bg-white/10 text-white/70 hover:text-white">
                <X size={14} />
              </button>
            )}
            <button onClick={() => searchRef.current?.focus()} aria-label="Поиск"
              className={`absolute right-1.5 top-1/2 flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-full transition-colors ${A.solid}`}>
              <Search size={16} />
            </button>
          </div>

          <div className="mt-3.5">
            <FilterChips state={state} update={update} reset={reset} activeCount={activeCount} t={t} A={A} />
          </div>
        </div>
      </section>

      {/* ── Таблица ────────────────────────────────────────────────────── */}
      <main className="flex min-h-0 min-w-0 flex-1 flex-col">
        {isError ? (
          <div className={`flex flex-1 flex-col items-center justify-center px-4 text-center ${t.muted}`}>
            <p className="font-medium">Не удалось загрузить данные</p>
            <p className={`mt-1 text-xs ${t.faint}`}>Проверьте, что API запущен, и попробуйте снова</p>
            <button onClick={() => refetch()} className={`mt-3 rounded-full border px-4 py-1.5 text-xs ${t.btn}`}>
              Повторить
            </button>
          </div>
        ) : (
          <div className="min-h-0 flex-1 overflow-auto">
            <BondTable items={items} loading={isFetching} sortBy={state.sortBy} sortOrder={state.sortOrder}
              onSort={toggleSort} onOpen={openBond} onReset={reset} selected={selected} t={t} A={A} dark={dark} />
          </div>
        )}
        <div className={`flex flex-wrap items-center justify-between gap-2 border-t px-4 py-2.5 sm:px-6 ${t.border}`}>
          <span className={`text-xs ${t.faint}`}>
            {total > 0 && <>Показаны {fmtInt(from)}–{fmtInt(to)} из {fmtInt(total)}</>}
          </span>
          <div className="flex items-center gap-4">
            {/* Строк на страницу: на больших мониторах 20 строк не заполняют таблицу */}
            <div className={`hidden items-center gap-1 text-xs sm:flex ${t.faint}`}>
              <span className="mr-1">Строк:</span>
              {PER_PAGE_OPTIONS.map((n) => (
                <button key={n} onClick={() => update({ perPage: n })}
                  className={`rounded-md px-1.5 py-0.5 font-medium transition-colors ${
                    state.perPage === n ? `${A.soft} ${A.text}` : `${t.muted} ${A.hover}`}`}>
                  {n}
                </button>
              ))}
            </div>
            <Pagination page={page} pages={pages} onPage={(p) => update({ page: p }, false)} t={t} A={A} />
          </div>
        </div>
      </main>
    </div>
  );
}
