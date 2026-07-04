import React, { useMemo, useState, useEffect, useRef } from "react";
import {
  Search, Sun, Moon, RotateCcw, ChevronLeft, ChevronRight, ChevronDown,
  ArrowUp, ArrowDown, ArrowUpDown, Landmark, Building2, MapPin, Lock,
  SlidersHorizontal, X, ArrowLeft, Palette, Check, CalendarDays,
  LayoutDashboard, Table2, CreditCard, TrendingUp, Zap,
} from "lucide-react";
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip as RTooltip,
  CartesianGrid, PieChart, Pie, Cell,
} from "recharts";

/* ============================================================
   МОКОВЫЕ ДАННЫЕ — поля соответствуют модели Bond из API.md.
   В продакшене заменяются на GET /api/v1/bonds (TanStack Query).
   ============================================================ */
const TODAY = new Date(2026, 6, 2);

function mulberry32(seed) {
  return function () {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const hashStr = (s) => [...s].reduce((a, c) => a + c.charCodeAt(0) * 7, 0);

function makeBonds() {
  const rnd = mulberry32(42);
  const bonds = [];
  let id = 1;
  const add = (b) => {
    const matDate = new Date(TODAY.getTime() + b.days_to_maturity * 864e5);
    bonds.push({
      id: id++, isin: b.secid, face_value: 1000, lot_size: 1,
      accrued_int: +(b.coupon_value * rnd()).toFixed(2),
      duration: Math.round(b.days_to_maturity * (0.6 + rnd() * 0.3)),
      offer_date: null, mat_date: matDate, ...b,
    });
  };

  // ОФЗ (TQOB)
  [26238, 26243, 26245, 26248, 29014, 52005].forEach((num) => {
    const days = Math.floor(300 + rnd() * 4000);
    const coupon = +(6.5 + rnd() * 6).toFixed(2);
    add({
      secid: `SU${num}RMFS`, short_name: `ОФЗ ${num}`, board_id: "TQOB",
      security_type: "ofz", prev_price: +(64 + rnd() * 38).toFixed(2),
      yield_at_prev_wa_price: +(12.3 + rnd() * 3.4).toFixed(2),
      coupon_percent: coupon, coupon_value: +((coupon / 2) * 10).toFixed(2),
      coupon_frequency: 2, days_to_maturity: days, list_level: 1,
      qualified_only: false, volume_today: 80e6 + rnd() * 900e6,
    });
  });

  // Корпоративные (TQCB)
  ["Магнит", "Сбер", "ГазпромК", "РЖД", "МТС", "Самолет", "Северсталь",
   "Европлан", "Сегежа", "Делимобиль", "ВУШ", "Селектел", "X5 Финанс", "КАМАЗ",
  ].forEach((name, i) => {
    const series = `${1 + (i % 4)}P${String(1 + Math.floor(rnd() * 12)).padStart(2, "0")}`;
    const days = Math.floor(60 + rnd() * 2500);
    const coupon = +(9.5 + rnd() * 11).toFixed(2);
    const freq = rnd() > 0.5 ? 4 : rnd() > 0.25 ? 2 : 12;
    const level = rnd() > 0.5 ? 1 : rnd() > 0.4 ? 2 : 3;
    add({
      secid: `RU000A1${String(10 + i * 3)}${["Z", "K", "M", "R"][i % 4]}${(i % 9) + 1}`,
      short_name: `${name}${series}`, board_id: "TQCB", security_type: "corp",
      prev_price: +(85 + rnd() * 21).toFixed(2),
      yield_at_prev_wa_price: +(13 + rnd() * 12 + (level - 1) * 2).toFixed(2),
      coupon_percent: coupon, coupon_value: +((coupon / freq) * 10).toFixed(2),
      coupon_frequency: freq, days_to_maturity: days, list_level: level,
      qualified_only: level === 3 && rnd() > 0.5, volume_today: 5e5 + rnd() * 6e7,
    });
  });

  // Муниципальные (TQIR)
  ["Мос.Обл", "СПб Гор", "Новосиб", "Якутия"].forEach((name, i) => {
    const days = Math.floor(200 + rnd() * 1700);
    const coupon = +(8.5 + rnd() * 5.5).toFixed(2);
    add({
      secid: `RU000A0M2${i}X${i + 1}`, short_name: `${name}.${34010 + i}`,
      board_id: "TQIR", security_type: "muni",
      prev_price: +(89 + rnd() * 13).toFixed(2),
      yield_at_prev_wa_price: +(13.5 + rnd() * 4.2).toFixed(2),
      coupon_percent: coupon, coupon_value: +((coupon / 4) * 10).toFixed(2),
      coupon_frequency: 4, days_to_maturity: days,
      list_level: rnd() > 0.5 ? 1 : 2, qualified_only: false,
      volume_today: 3e5 + rnd() * 8e6,
    });
  });

  return bonds;
}
const BONDS = makeBonds();

function couponSchedule(b) {
  const step = Math.round(365 / b.coupon_frequency);
  const res = [];
  let d = new Date(TODAY);
  for (let i = 0; i < 10; i++) {
    d = new Date(d.getTime() + step * 864e5);
    if (d >= b.mat_date) break;
    res.push(new Date(d));
  }
  res.push(b.mat_date);
  return res.slice(0, 10);
}

function priceHistory(b) {
  const rnd = mulberry32(hashStr(b.secid));
  let p = b.prev_price;
  const raw = [p];
  for (let i = 0; i < 89; i++) raw.push(raw[raw.length - 1] + (rnd() - 0.5) * 0.5);
  const shift = b.prev_price - raw[89];
  return raw.map((v, i) => {
    const d = new Date(TODAY.getTime() - (89 - i) * 864e5);
    return {
      date: d.toLocaleDateString("ru-RU", { day: "numeric", month: "short" }),
      price: +(v + (shift * i) / 89).toFixed(2),
    };
  });
}

/* ============================================================
   Форматирование и справочники
   ============================================================ */
const fmt = (n, d = 2) => (n == null ? "—" : n.toLocaleString("ru-RU", { minimumFractionDigits: d, maximumFractionDigits: d }));
const fmtDate = (d) => (d ? d.toLocaleDateString("ru-RU", { day: "2-digit", month: "2-digit", year: "numeric" }) : "—");
const fmtVol = (v) => v >= 1e9 ? `${(v / 1e9).toLocaleString("ru-RU", { maximumFractionDigits: 1 })} млрд`
  : v >= 1e6 ? `${(v / 1e6).toLocaleString("ru-RU", { maximumFractionDigits: 1 })} млн`
  : `${(v / 1e3).toLocaleString("ru-RU", { maximumFractionDigits: 0 })} тыс`;
const plural = (n, one, few, many) => {
  const m10 = n % 10, m100 = n % 100;
  if (m10 === 1 && m100 !== 11) return one;
  if (m10 >= 2 && m10 <= 4 && (m100 < 10 || m100 >= 20)) return few;
  return many;
};

const TYPE_META = {
  ofz: { label: "ОФЗ", full: "Государственные (ОФЗ)", Icon: Landmark, hex: "#0ea5e9" },
  corp: { label: "Корп.", full: "Корпоративные", Icon: Building2, hex: "#10b981" },
  muni: { label: "Муни.", full: "Муниципальные", Icon: MapPin, hex: "#f59e0b" },
};

/* ============================================================
   Темы: режим (тёмный/светлый) × акцентный цвет
   ============================================================ */
const ACCENTS = {
  emerald: { name: "Изумруд", dot: "bg-emerald-500", hex: "#10b981",
    dark: { solid: "bg-emerald-500 text-zinc-950 hover:bg-emerald-400", text: "text-emerald-400", chipOn: "bg-emerald-500 text-zinc-950 border-emerald-500", soft: "bg-emerald-950 text-emerald-400", focus: "focus:border-emerald-500", hover: "hover:text-emerald-400", border: "border-emerald-500" },
    light: { solid: "bg-emerald-600 text-white hover:bg-emerald-500", text: "text-emerald-600", chipOn: "bg-emerald-600 text-white border-emerald-600", soft: "bg-emerald-100 text-emerald-700", focus: "focus:border-emerald-600", hover: "hover:text-emerald-600", border: "border-emerald-600" } },
  sky: { name: "Синий", dot: "bg-sky-500", hex: "#0ea5e9",
    dark: { solid: "bg-sky-500 text-zinc-950 hover:bg-sky-400", text: "text-sky-400", chipOn: "bg-sky-500 text-zinc-950 border-sky-500", soft: "bg-sky-950 text-sky-400", focus: "focus:border-sky-500", hover: "hover:text-sky-400", border: "border-sky-500" },
    light: { solid: "bg-sky-600 text-white hover:bg-sky-500", text: "text-sky-600", chipOn: "bg-sky-600 text-white border-sky-600", soft: "bg-sky-100 text-sky-700", focus: "focus:border-sky-600", hover: "hover:text-sky-600", border: "border-sky-600" } },
  violet: { name: "Фиолетовый", dot: "bg-violet-500", hex: "#8b5cf6",
    dark: { solid: "bg-violet-500 text-white hover:bg-violet-400", text: "text-violet-400", chipOn: "bg-violet-500 text-white border-violet-500", soft: "bg-violet-950 text-violet-400", focus: "focus:border-violet-500", hover: "hover:text-violet-400", border: "border-violet-500" },
    light: { solid: "bg-violet-600 text-white hover:bg-violet-500", text: "text-violet-600", chipOn: "bg-violet-600 text-white border-violet-600", soft: "bg-violet-100 text-violet-700", focus: "focus:border-violet-600", hover: "hover:text-violet-600", border: "border-violet-600" } },
  amber: { name: "Янтарь", dot: "bg-amber-500", hex: "#f59e0b",
    dark: { solid: "bg-amber-500 text-zinc-950 hover:bg-amber-400", text: "text-amber-400", chipOn: "bg-amber-500 text-zinc-950 border-amber-500", soft: "bg-amber-950 text-amber-400", focus: "focus:border-amber-500", hover: "hover:text-amber-400", border: "border-amber-500" },
    light: { solid: "bg-amber-500 text-white hover:bg-amber-400", text: "text-amber-600", chipOn: "bg-amber-500 text-white border-amber-500", soft: "bg-amber-100 text-amber-700", focus: "focus:border-amber-500", hover: "hover:text-amber-600", border: "border-amber-500" } },
  rose: { name: "Роза", dot: "bg-rose-500", hex: "#f43f5e",
    dark: { solid: "bg-rose-500 text-white hover:bg-rose-400", text: "text-rose-400", chipOn: "bg-rose-500 text-white border-rose-500", soft: "bg-rose-950 text-rose-400", focus: "focus:border-rose-500", hover: "hover:text-rose-400", border: "border-rose-500" },
    light: { solid: "bg-rose-600 text-white hover:bg-rose-500", text: "text-rose-600", chipOn: "bg-rose-600 text-white border-rose-600", soft: "bg-rose-100 text-rose-700", focus: "focus:border-rose-600", hover: "hover:text-rose-600", border: "border-rose-600" } },
};

const makeTokens = (dark) => dark
  ? { page: "bg-zinc-950 text-zinc-100", header: "bg-zinc-950 border-zinc-800",
      panel: "bg-zinc-900 border-zinc-800", card: "bg-zinc-900 border-zinc-800",
      border: "border-zinc-800", muted: "text-zinc-400", faint: "text-zinc-500",
      strong: "text-zinc-100",
      input: "bg-zinc-950 border-zinc-800 text-zinc-100 placeholder-zinc-600",
      rowEven: "bg-zinc-900", rowOdd: "bg-zinc-950", rowHover: "hover:bg-zinc-800",
      thead: "bg-zinc-900 text-zinc-500 border-zinc-800",
      chipOff: "bg-transparent text-zinc-400 border-zinc-700 hover:border-zinc-500",
      btn: "border-zinc-700 text-zinc-300 hover:bg-zinc-800",
      soft: "bg-zinc-800", up: "text-emerald-400", down: "text-red-400",
      grid: "#27272a", axis: "#71717a", tooltipBg: "#18181b" }
  : { page: "bg-zinc-100 text-zinc-900", header: "bg-white border-zinc-200",
      panel: "bg-white border-zinc-200 shadow-sm", card: "bg-white border-zinc-200 shadow-sm",
      border: "border-zinc-200", muted: "text-zinc-500", faint: "text-zinc-400",
      strong: "text-zinc-900",
      input: "bg-white border-zinc-300 text-zinc-900 placeholder-zinc-400",
      rowEven: "bg-zinc-50", rowOdd: "bg-white", rowHover: "hover:bg-zinc-100",
      thead: "bg-zinc-50 text-zinc-500 border-zinc-200",
      chipOff: "bg-transparent text-zinc-500 border-zinc-300 hover:border-zinc-500",
      btn: "border-zinc-300 text-zinc-600 hover:bg-zinc-100",
      soft: "bg-zinc-100", up: "text-emerald-600", down: "text-red-600",
      grid: "#e4e4e7", axis: "#a1a1aa", tooltipBg: "#ffffff" };

const DEFAULT_FILTERS = {
  yieldMin: "", yieldMax: "", couponMin: "", couponMax: "", daysMin: "", daysMax: "",
  types: { ofz: true, corp: true, muni: true }, listLevelMax: 0, nonQualifiedOnly: false,
};
const PER_PAGE = 10;

/* ============================================================
   Переиспользуемые компоненты (вне App — иначе инпуты теряют фокус)
   ============================================================ */
function FilterSection({ title, badge, open, onToggle, children, t, A }) {
  return (
    <div className={`border-b last:border-b-0 ${t.border}`}>
      <button onClick={onToggle} className={`flex w-full items-center justify-between py-3 text-left text-xs font-semibold uppercase tracking-wider transition-colors ${A.hover}`}>
        <span className="flex items-center gap-2">
          {title}
          {badge > 0 && <span className={`rounded-full px-1.5 py-0.5 text-[10px] font-bold normal-case ${A.soft}`}>{badge}</span>}
        </span>
        <ChevronDown size={14} className={`transition-transform ${open ? "rotate-180" : ""}`} />
      </button>
      {open && <div className="pb-4">{children}</div>}
    </div>
  );
}

function RangePair({ minVal, maxVal, onMin, onMax, t, A }) {
  const cls = `w-full min-w-0 rounded-lg border px-2.5 py-1.5 text-sm outline-none transition-colors ${t.input} ${A.focus}`;
  return (
    <div className="flex gap-2">
      <input type="number" inputMode="decimal" placeholder="от" value={minVal} onChange={(e) => onMin(e.target.value)} className={cls} />
      <input type="number" inputMode="decimal" placeholder="до" value={maxVal} onChange={(e) => onMax(e.target.value)} className={cls} />
    </div>
  );
}

function ListLevelBadge({ level, dark }) {
  const p = dark
    ? ["bg-emerald-950 text-emerald-400", "bg-sky-950 text-sky-400", "bg-amber-950 text-amber-400"]
    : ["bg-emerald-100 text-emerald-700", "bg-sky-100 text-sky-700", "bg-amber-100 text-amber-700"];
  return <span className={`inline-flex h-6 w-6 items-center justify-center rounded-md text-xs font-bold ${p[level - 1]}`}>{level}</span>;
}

function Pagination({ page, pages, onPage, t, A }) {
  const nums = [...new Set([1, pages, page - 1, page, page + 1])].filter((n) => n >= 1 && n <= pages).sort((a, b) => a - b);
  return (
    <div className="flex items-center gap-1">
      <button onClick={() => onPage(Math.max(1, page - 1))} disabled={page === 1} aria-label="Назад"
        className={`flex h-8 w-8 items-center justify-center rounded-lg border transition-colors disabled:opacity-30 ${t.btn}`}>
        <ChevronLeft size={15} />
      </button>
      {nums.map((n, i) => (
        <React.Fragment key={n}>
          {i > 0 && n - nums[i - 1] > 1 && <span className={`px-1 ${t.faint}`}>…</span>}
          <button onClick={() => onPage(n)}
            className={`h-8 min-w-8 rounded-lg px-2 text-sm font-medium transition-colors ${n === page ? A.solid : `border ${t.btn}`}`}>
            {n}
          </button>
        </React.Fragment>
      ))}
      <button onClick={() => onPage(Math.min(pages, page + 1))} disabled={page === pages} aria-label="Вперёд"
        className={`flex h-8 w-8 items-center justify-center rounded-lg border transition-colors disabled:opacity-30 ${t.btn}`}>
        <ChevronRight size={15} />
      </button>
    </div>
  );
}

/* ============================================================
   Header
   ============================================================ */
function Header({ route, go, dark, setDark, accent, setAccent, t, A }) {
  const [pickerOpen, setPickerOpen] = useState(false);
  const nav = [
    { key: "screener", label: "Скринер", Icon: Table2 },
    { key: "dashboard", label: "Дашборд", Icon: LayoutDashboard },
    { key: "pricing", label: "Тарифы", Icon: CreditCard },
  ];
  const active = route;
  return (
    <header className={`sticky top-0 z-30 border-b ${t.header}`}>
      <div className="mx-auto flex h-14 max-w-7xl items-center gap-4 px-4">
        <button onClick={() => go("screener")} className="flex items-center gap-2 font-bold tracking-tight">
          <span className={`flex h-7 w-7 items-center justify-center rounded-lg ${A.solid}`}>
            <TrendingUp size={15} strokeWidth={2.5} />
          </span>
          <span className="hidden text-[15px] sm:block">Bond Screener</span>
        </button>
        <nav className="flex gap-1 text-sm">
          {nav.map(({ key, label, Icon }) => (
            <button key={key} onClick={() => go(key)}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 transition-colors ${
                active === key ? `font-semibold ${A.soft}` : `${t.muted} ${A.hover}`}`}>
              <Icon size={14} /> <span className="hidden md:inline">{label}</span>
            </button>
          ))}
        </nav>
        <div className="relative ml-auto flex items-center gap-2">
          <button onClick={() => setPickerOpen((v) => !v)} aria-label="Настройки темы"
            className={`flex h-8 w-8 items-center justify-center rounded-lg border transition-colors ${t.btn} ${pickerOpen ? A.border : ""}`}>
            <Palette size={15} />
          </button>
          {pickerOpen && (
            <div className={`absolute right-0 top-10 w-56 rounded-xl border p-3 shadow-lg ${t.panel}`}>
              <div className={`mb-2 text-xs font-semibold uppercase tracking-wider ${t.faint}`}>Режим</div>
              <div className={`mb-3 grid grid-cols-2 gap-1 rounded-lg p-1 ${t.soft}`}>
                {[{ v: false, l: "Светлый", I: Sun }, { v: true, l: "Тёмный", I: Moon }].map(({ v, l, I }) => (
                  <button key={l} onClick={() => setDark(v)}
                    className={`flex items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium transition-colors ${
                      dark === v ? A.solid : t.muted}`}>
                    <I size={12} /> {l}
                  </button>
                ))}
              </div>
              <div className={`mb-2 text-xs font-semibold uppercase tracking-wider ${t.faint}`}>Акцент</div>
              <div className="flex gap-2">
                {Object.entries(ACCENTS).map(([key, a]) => (
                  <button key={key} onClick={() => setAccent(key)} title={a.name} aria-label={a.name}
                    className={`flex h-7 w-7 items-center justify-center rounded-full ${a.dot} transition-transform hover:scale-110`}>
                    {accent === key && <Check size={13} className="text-white" strokeWidth={3} />}
                  </button>
                ))}
              </div>
            </div>
          )}
          <button className={`hidden rounded-lg px-3.5 py-1.5 text-sm font-semibold transition-colors sm:block ${A.solid}`}>
            Войти
          </button>
        </div>
      </div>
    </header>
  );
}

/* ============================================================
   Страница: Скринер
   ============================================================ */
const COLUMNS = [
  { key: "short_name", label: "Название", align: "left" },
  { key: "prev_price", label: "Цена, %", align: "right" },
  { key: "yield_at_prev_wa_price", label: "Доходность", align: "right" },
  { key: "coupon_percent", label: "Купон, %", align: "right" },
  { key: "days_to_maturity", label: "Погашение", align: "right" },
  { key: "volume_today", label: "Объём, ₽", align: "right" },
  { key: "list_level", label: "Листинг", align: "center" },
];

function ScreenerPage({ st, t, A, dark, openBond, selected }) {
  const { filters, setFilters, search, setSearch, sort, setSort, page, setPage } = st;
  const [showFilters, setShowFilters] = useState(true);
  const [sections, setSections] = useState({ yield: true, coupon: false, days: false, type: false, listing: false });
  const [loading, setLoading] = useState(false);
  const first = useRef(true);

  useEffect(() => {
    if (first.current) { first.current = false; return; }
    setLoading(true);
    const id = setTimeout(() => setLoading(false), 250);
    return () => clearTimeout(id);
  }, [filters, search, sort, page]);

  const setF = (patch) => { setFilters((p) => ({ ...p, ...patch })); setPage(1); };

  const filtered = useMemo(() => {
    const f = filters, q = search.trim().toLowerCase();
    const num = (v) => (v === "" ? null : Number(v));
    return BONDS.filter((b) => {
      if (!f.types[b.security_type]) return false;
      const checks = [
        [num(f.yieldMin), (x) => b.yield_at_prev_wa_price >= x], [num(f.yieldMax), (x) => b.yield_at_prev_wa_price <= x],
        [num(f.couponMin), (x) => b.coupon_percent >= x], [num(f.couponMax), (x) => b.coupon_percent <= x],
        [num(f.daysMin), (x) => b.days_to_maturity >= x], [num(f.daysMax), (x) => b.days_to_maturity <= x],
      ];
      for (const [v, ok] of checks) if (v != null && !ok(v)) return false;
      if (f.listLevelMax > 0 && b.list_level > f.listLevelMax) return false;
      if (f.nonQualifiedOnly && b.qualified_only) return false;
      if (q && !b.short_name.toLowerCase().includes(q) && !b.secid.toLowerCase().includes(q)) return false;
      return true;
    });
  }, [filters, search]);

  const sorted = useMemo(() => {
    const dir = sort.order === "asc" ? 1 : -1;
    return [...filtered].sort((a, b) =>
      typeof a[sort.field] === "string"
        ? a[sort.field].localeCompare(b[sort.field], "ru") * dir
        : (a[sort.field] - b[sort.field]) * dir);
  }, [filtered, sort]);

  const pages = Math.max(1, Math.ceil(sorted.length / PER_PAGE));
  const safePage = Math.min(page, pages);
  const items = sorted.slice((safePage - 1) * PER_PAGE, safePage * PER_PAGE);
  const avgYield = filtered.length ? filtered.reduce((s, b) => s + b.yield_at_prev_wa_price, 0) / filtered.length : 0;

  const activeCount =
    ["yieldMin", "yieldMax", "couponMin", "couponMax", "daysMin", "daysMax"].filter((k) => filters[k] !== "").length +
    (Object.values(filters.types).some((v) => !v) ? 1 : 0) +
    (filters.listLevelMax > 0 ? 1 : 0) + (filters.nonQualifiedOnly ? 1 : 0);

  const reset = () => { setFilters(DEFAULT_FILTERS); setSearch(""); setPage(1); };
  const toggleSort = (field) =>
    setSort((s) => s.field === field ? { field, order: s.order === "desc" ? "asc" : "desc" } : { field, order: "desc" });
  const toggleSec = (k) => setSections((s) => ({ ...s, [k]: !s[k] }));

  return (
    <div className="mx-auto max-w-7xl px-4 py-5">
      {/* Тулбар */}
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center">
        <button onClick={() => setShowFilters((v) => !v)}
          className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${showFilters ? A.chipOn : `${t.btn}`}`}>
          <SlidersHorizontal size={14} />
          Фильтры
          {activeCount > 0 && (
            <span className={`rounded-full px-1.5 text-[11px] font-bold ${showFilters ? "bg-black/15" : A.soft}`}>{activeCount}</span>
          )}
        </button>
        <div className="relative flex-1">
          <Search size={15} className={`pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 ${t.faint}`} />
          <input value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Название или тикер…"
            className={`w-full rounded-lg border py-2 pl-9 pr-8 text-sm outline-none transition-colors ${t.input} ${A.focus}`} />
          {search && (
            <button onClick={() => setSearch("")} aria-label="Очистить поиск"
              className={`absolute right-2 top-1/2 -translate-y-1/2 ${t.faint} hover:opacity-70`}>
              <X size={14} />
            </button>
          )}
        </div>
        <div className={`flex items-center gap-4 text-sm ${t.muted}`}>
          <span><b className={t.strong}>{filtered.length}</b> {plural(filtered.length, "бумага", "бумаги", "бумаг")}</span>
          {filtered.length > 0 && <span>ср. доходность <b className={t.up}>{fmt(avgYield)}%</b></span>}
        </div>
      </div>

      <div className="flex flex-col gap-5 lg:flex-row">
        {/* Панель фильтров (сворачиваемая) */}
        {showFilters && (
          <aside className={`h-fit w-full shrink-0 rounded-2xl border px-4 py-1 lg:w-64 ${t.panel}`}>
            <FilterSection title="Доходность, %" t={t} A={A} open={sections.yield} onToggle={() => toggleSec("yield")}
              badge={(filters.yieldMin !== "") + (filters.yieldMax !== "")}>
              <RangePair t={t} A={A} minVal={filters.yieldMin} maxVal={filters.yieldMax}
                onMin={(v) => setF({ yieldMin: v })} onMax={(v) => setF({ yieldMax: v })} />
            </FilterSection>
            <FilterSection title="Купон, %" t={t} A={A} open={sections.coupon} onToggle={() => toggleSec("coupon")}
              badge={(filters.couponMin !== "") + (filters.couponMax !== "")}>
              <RangePair t={t} A={A} minVal={filters.couponMin} maxVal={filters.couponMax}
                onMin={(v) => setF({ couponMin: v })} onMax={(v) => setF({ couponMax: v })} />
            </FilterSection>
            <FilterSection title="Срок, дней" t={t} A={A} open={sections.days} onToggle={() => toggleSec("days")}
              badge={(filters.daysMin !== "") + (filters.daysMax !== "")}>
              <RangePair t={t} A={A} minVal={filters.daysMin} maxVal={filters.daysMax}
                onMin={(v) => setF({ daysMin: v })} onMax={(v) => setF({ daysMax: v })} />
            </FilterSection>
            <FilterSection title="Тип бумаги" t={t} A={A} open={sections.type} onToggle={() => toggleSec("type")}
              badge={Object.values(filters.types).filter((v) => !v).length}>
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(TYPE_META).map(([key, { label, Icon }]) => (
                  <button key={key} onClick={() => setF({ types: { ...filters.types, [key]: !filters.types[key] } })}
                    className={`flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs font-medium transition-colors ${
                      filters.types[key] ? A.chipOn : t.chipOff}`}>
                    <Icon size={12} /> {label}
                  </button>
                ))}
              </div>
            </FilterSection>
            <FilterSection title="Листинг и доступ" t={t} A={A} open={sections.listing} onToggle={() => toggleSec("listing")}
              badge={(filters.listLevelMax > 0 ? 1 : 0) + (filters.nonQualifiedOnly ? 1 : 0)}>
              <div className="mb-2 flex gap-1.5">
                {[0, 1, 2, 3].map((lvl) => (
                  <button key={lvl} onClick={() => setF({ listLevelMax: lvl })}
                    className={`flex-1 rounded-lg border py-1.5 text-xs font-medium transition-colors ${
                      filters.listLevelMax === lvl ? A.chipOn : t.chipOff}`}>
                    {lvl === 0 ? "Все" : `≤${lvl}`}
                  </button>
                ))}
              </div>
              <label className="flex cursor-pointer items-center gap-2.5 select-none pt-1">
                <input type="checkbox" checked={filters.nonQualifiedOnly}
                  onChange={(e) => setF({ nonQualifiedOnly: e.target.checked })}
                  className="h-4 w-4" style={{ accentColor: A.hex }} />
                <span className="text-sm">Только для неквал.</span>
              </label>
            </FilterSection>
            <button onClick={reset} disabled={activeCount === 0 && !search}
              className={`my-3 flex w-full items-center justify-center gap-1.5 rounded-lg border py-2 text-xs font-medium transition-colors disabled:opacity-40 ${t.btn}`}>
              <RotateCcw size={12} /> Сбросить всё
            </button>
          </aside>
        )}

        {/* Таблица */}
        <main className="min-w-0 flex-1">
          <div className={`overflow-hidden rounded-2xl border ${t.panel}`}>
            <div className="max-h-[540px] overflow-auto">
              <table className={`w-full border-collapse text-sm transition-opacity duration-150 ${loading ? "opacity-50" : "opacity-100"}`}>
                <thead className={`sticky top-0 z-10 border-b text-xs ${t.thead}`}>
                  <tr>
                    {COLUMNS.map((c) => (
                      <th key={c.key} onClick={() => toggleSort(c.key)}
                        className={`cursor-pointer select-none whitespace-nowrap px-3 py-2.5 font-semibold uppercase tracking-wide transition-colors ${A.hover} ${
                          c.align === "right" ? "text-right" : c.align === "center" ? "text-center" : "text-left"}`}>
                        <span className={`inline-flex items-center gap-1 ${c.align === "right" ? "flex-row-reverse" : ""}`}>
                          {c.label}
                          {sort.field === c.key
                            ? sort.order === "desc" ? <ArrowDown size={12} className={A.text} /> : <ArrowUp size={12} className={A.text} />
                            : <ArrowUpDown size={12} className="opacity-40" />}
                        </span>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {items.length === 0 && (
                    <tr><td colSpan={COLUMNS.length} className={`px-4 py-14 text-center ${t.muted}`}>
                      <p className="font-medium">Ничего не найдено</p>
                      <p className={`mt-1 text-xs ${t.faint}`}>Смягчите условия или сбросьте фильтры</p>
                      <button onClick={reset} className={`mt-3 rounded-lg border px-3 py-1.5 text-xs ${t.btn}`}>Сбросить фильтры</button>
                    </td></tr>
                  )}
                  {items.map((b, i) => {
                    const { label, Icon } = TYPE_META[b.security_type];
                    return (
                      <tr key={b.secid} onClick={() => openBond(b.secid)}
                        className={`cursor-pointer border-b transition-colors last:border-b-0 ${t.border} ${
                          selected === b.secid ? A.soft : `${i % 2 ? t.rowEven : t.rowOdd} ${t.rowHover}`}`}>
                        <td className="px-3 py-2.5">
                          <div className="flex items-center gap-2.5">
                            <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${t.soft} ${t.muted}`}>
                              <Icon size={14} />
                            </span>
                            <div className="min-w-0">
                              <div className={`flex items-center gap-1.5 font-medium ${A.hover}`}>
                                <span className="truncate">{b.short_name}</span>
                                {b.qualified_only && <Lock size={11} className={t.faint} />}
                              </div>
                              <div className={`font-mono text-[11px] ${t.faint}`}>{b.secid}</div>
                            </div>
                          </div>
                        </td>
                        <td className="whitespace-nowrap px-3 py-2.5 text-right tabular-nums">{fmt(b.prev_price)}</td>
                        <td className={`whitespace-nowrap px-3 py-2.5 text-right font-semibold tabular-nums ${b.yield_at_prev_wa_price >= 16 ? t.up : ""}`}>
                          {fmt(b.yield_at_prev_wa_price)}%
                        </td>
                        <td className="whitespace-nowrap px-3 py-2.5 text-right tabular-nums">
                          {fmt(b.coupon_percent)}<span className={`ml-1 text-[11px] ${t.faint}`}>×{b.coupon_frequency}</span>
                        </td>
                        <td className="whitespace-nowrap px-3 py-2.5 text-right tabular-nums">
                          <div>{b.days_to_maturity.toLocaleString("ru-RU")} дн.</div>
                          <div className={`text-[11px] ${t.faint}`}>{fmtDate(b.mat_date)}</div>
                        </td>
                        <td className={`whitespace-nowrap px-3 py-2.5 text-right tabular-nums ${t.muted}`}>{fmtVol(b.volume_today)}</td>
                        <td className="px-3 py-2.5 text-center"><ListLevelBadge level={b.list_level} dark={dark} /></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <div className={`flex items-center justify-between border-t px-3 py-2.5 ${t.border}`}>
              <span className={`text-xs ${t.faint}`}>
                {filtered.length > 0 && <>Показаны {(safePage - 1) * PER_PAGE + 1}–{Math.min(safePage * PER_PAGE, filtered.length)} из {filtered.length}</>}
              </span>
              <Pagination page={safePage} pages={pages} onPage={setPage} t={t} A={A} />
            </div>
          </div>
          <p className={`mt-3 text-xs ${t.faint}`}>
            Прототип: данные моковые. В продакшене фильтрацию и сортировку выполняет бэкенд — GET /api/v1/bonds.
          </p>
        </main>
      </div>
    </div>
  );
}

/* ============================================================
   Боковая панель: детали облигации (открывается поверх таблицы,
   клик по другой строке меняет содержимое без закрытия)
   ============================================================ */
function BondDrawer({ secid, onClose, onSelect, t, A, dark }) {
  const [tab, setTab] = useState("main");
  const scrollRef = useRef(null);
  const b = BONDS.find((x) => x.secid === secid) || null;

  useEffect(() => {
    setTab("main");
    if (scrollRef.current) scrollRef.current.scrollTop = 0;
  }, [secid]);

  useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const history = useMemo(() => (b ? priceHistory(b) : []), [secid]);
  const similar = useMemo(() => !b ? [] :
    BONDS.filter((x) => x.security_type === b.security_type && x.secid !== b.secid)
      .sort((x, y) =>
        Math.abs(x.yield_at_prev_wa_price - b.yield_at_prev_wa_price) -
        Math.abs(y.yield_at_prev_wa_price - b.yield_at_prev_wa_price))
      .slice(0, 5), [secid]);

  if (!b) return null;
  const { label, full, Icon } = TYPE_META[b.security_type];
  const schedule = couponSchedule(b);

  const stats = [
    { label: "Цена", value: `${fmt(b.prev_price)}%`, sub: `НКД ${fmt(b.accrued_int)} ₽` },
    { label: "Доходность", value: `${fmt(b.yield_at_prev_wa_price)}%`, accent: true, sub: "к погашению" },
    { label: "Купон", value: `${fmt(b.coupon_value)} ₽`, sub: `${fmt(b.coupon_percent)}% · ${b.coupon_frequency} р/год` },
    { label: "До погашения", value: `${b.days_to_maturity.toLocaleString("ru-RU")} дн.`, sub: fmtDate(b.mat_date) },
  ];

  const mainRows = [
    ["ISIN", b.isin], ["Борд MOEX", b.board_id], ["Тип", full],
    ["Номинал", `${fmt(b.face_value, 0)} ₽`], ["Размер лота", `${b.lot_size} шт.`],
    ["НКД", `${fmt(b.accrued_int)} ₽`], ["Дюрация", `${b.duration.toLocaleString("ru-RU")} дн.`],
    ["Дата оферты", fmtDate(b.offer_date)], ["Уровень листинга", b.list_level],
    ["Доступ", b.qualified_only ? "Только квалифицированные" : "Все инвесторы"],
    ["Объём торгов за день", `${fmtVol(b.volume_today)} ₽`],
  ];

  const tabs = [
    { key: "main", label: "Основное" }, { key: "coupons", label: "Купоны" },
    { key: "history", label: "История" }, { key: "similar", label: "Похожие" },
  ];

  return (
    <>
      {/* Подложка только на мобильных: на десктопе таблица остаётся кликабельной */}
      <div className="fixed inset-0 z-30 lg:hidden" style={{ background: "rgba(0,0,0,.45)" }} onClick={onClose} />
      <aside
        className={`drawer-in fixed inset-y-0 right-0 z-40 flex w-full max-w-md flex-col border-l shadow-2xl ${t.panel}`}
        role="dialog" aria-label={`Облигация ${b.short_name}`}>
        {/* Шапка */}
        <div className={`flex items-start justify-between gap-3 border-b p-4 ${t.border}`}>
          <div className="flex min-w-0 items-center gap-3">
            <span className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${A.soft}`}><Icon size={18} /></span>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <h2 className="truncate text-base font-bold tracking-tight">{b.short_name}</h2>
                <span className={`shrink-0 rounded-full px-2 py-0.5 text-[11px] font-medium ${A.soft}`}>{label}</span>
                {b.qualified_only && (
                  <span className={`flex shrink-0 items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium ${dark ? "bg-amber-950 text-amber-400" : "bg-amber-100 text-amber-700"}`}>
                    <Lock size={9} /> квал.
                  </span>
                )}
              </div>
              <div className={`font-mono text-[11px] ${t.faint}`}>{b.secid}</div>
            </div>
          </div>
          <button onClick={onClose} aria-label="Закрыть панель"
            className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border transition-colors ${t.btn}`}>
            <X size={15} />
          </button>
        </div>

        {/* Табы */}
        <div className={`flex gap-1 border-b px-4 ${t.border}`}>
          {tabs.map(({ key, label }) => (
            <button key={key} onClick={() => setTab(key)}
              className={`-mb-px border-b-2 px-3 py-2 text-sm font-medium transition-colors ${
                tab === key ? `${A.border} ${A.text}` : `border-transparent ${t.muted} ${A.hover}`}`}>
              {label}
            </button>
          ))}
        </div>

        {/* Прокручиваемое содержимое */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-4">
          {/* Ключевые показатели — всегда сверху */}
          <div className="mb-4 grid grid-cols-2 gap-2">
            {stats.map((s) => (
              <div key={s.label} className={`rounded-xl border p-3 ${t.card}`}>
                <div className={`text-[11px] ${t.faint}`}>{s.label}</div>
                <div className={`mt-0.5 text-lg font-bold tabular-nums ${s.accent ? A.text : ""}`}>{s.value}</div>
                {s.sub && <div className={`text-[11px] ${t.muted}`}>{s.sub}</div>}
              </div>
            ))}
          </div>

          {tab === "main" && (
            <div className={`overflow-hidden rounded-xl border ${t.card}`}>
              {mainRows.map(([k, v], i) => (
                <div key={k} className={`flex items-baseline justify-between gap-4 px-3.5 py-2.5 ${i < mainRows.length - 1 ? `border-b ${t.border}` : ""}`}>
                  <span className={`text-sm ${t.muted}`}>{k}</span>
                  <span className="text-right text-sm font-medium tabular-nums">{v}</span>
                </div>
              ))}
            </div>
          )}

          {tab === "coupons" && (
            <div className={`overflow-hidden rounded-xl border ${t.card}`}>
              <div className={`flex items-center gap-2 border-b px-3.5 py-2.5 text-sm font-semibold ${t.border}`}>
                <CalendarDays size={14} className={A.text} /> Ближайшие выплаты
              </div>
              {schedule.map((d, i) => {
                const isLast = i === schedule.length - 1 && d.getTime() === b.mat_date.getTime();
                return (
                  <div key={i} className={`flex items-center justify-between gap-2 px-3.5 py-2.5 text-sm ${i % 2 ? t.rowEven : t.rowOdd}`}>
                    <span className="tabular-nums">{fmtDate(d)}</span>
                    <span className={`min-w-0 truncate text-[11px] ${t.faint}`}>{isLast ? "купон + номинал" : `купон №${i + 1}`}</span>
                    <span className="font-semibold tabular-nums">{fmt(isLast ? b.coupon_value + b.face_value : b.coupon_value)} ₽</span>
                  </div>
                );
              })}
            </div>
          )}

          {tab === "history" && (
            <div className={`rounded-xl border p-3.5 ${t.card}`}>
              <div className="mb-2 text-sm font-semibold">Цена за 90 дней, % от номинала</div>
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={history} margin={{ top: 4, right: 4, bottom: 0, left: -18 }}>
                    <defs>
                      <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor={A.hex} stopOpacity={0.28} />
                        <stop offset="100%" stopColor={A.hex} stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid stroke={t.grid} strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="date" tick={{ fontSize: 10, fill: t.axis }} tickLine={false} axisLine={false} minTickGap={44} />
                    <YAxis domain={["auto", "auto"]} tick={{ fontSize: 10, fill: t.axis }} tickLine={false} axisLine={false} />
                    <RTooltip contentStyle={{ background: t.tooltipBg, border: `1px solid ${t.grid}`, borderRadius: 10, fontSize: 12 }}
                      formatter={(v) => [`${fmt(v)}%`, "Цена"]} />
                    <Area type="monotone" dataKey="price" stroke={A.hex} strokeWidth={2} fill="url(#priceFill)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {tab === "similar" && (
            <div className={`overflow-hidden rounded-xl border ${t.card}`}>
              {similar.map((s, i) => (
                <button key={s.secid} onClick={() => onSelect(s.secid)}
                  className={`flex w-full items-center justify-between gap-3 px-3.5 py-2.5 text-left text-sm transition-colors ${i % 2 ? t.rowEven : t.rowOdd} ${t.rowHover}`}>
                  <div className="min-w-0">
                    <div className="truncate font-medium">{s.short_name}</div>
                    <div className={`font-mono text-[10px] ${t.faint}`}>{s.secid}</div>
                  </div>
                  <div className="flex shrink-0 items-center gap-3 tabular-nums">
                    <span className={`font-semibold ${t.up}`}>{fmt(s.yield_at_prev_wa_price)}%</span>
                    <span className={`text-xs ${t.faint}`}>{s.days_to_maturity} дн.</span>
                    <ChevronRight size={14} className={t.faint} />
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </aside>
    </>
  );
}

/* ============================================================
   Страница: Дашборд
   ============================================================ */
function DashboardPage({ t, A, openBond }) {
  const total = BONDS.length;
  const avg = (f) => BONDS.reduce((s, b) => s + f(b), 0) / total;
  const byType = Object.keys(TYPE_META).map((k) => ({
    key: k, name: TYPE_META[k].full, value: BONDS.filter((b) => b.security_type === k).length, hex: TYPE_META[k].hex,
  }));
  const topYield = [...BONDS].sort((a, b) => b.yield_at_prev_wa_price - a.yield_at_prev_wa_price).slice(0, 5);
  const topCoupon = [...BONDS].sort((a, b) => b.coupon_percent - a.coupon_percent).slice(0, 5);

  const cards = [
    { label: "Всего облигаций", value: total.toLocaleString("ru-RU") },
    { label: "Средняя доходность", value: `${fmt(avg((b) => b.yield_at_prev_wa_price))}%`, accent: true },
    { label: "Средний купон", value: `${fmt(avg((b) => b.coupon_percent))}%` },
    { label: "Средняя дюрация", value: `${Math.round(avg((b) => b.duration)).toLocaleString("ru-RU")} дн.` },
  ];

  const TopList = ({ title, items, valueOf }) => (
    <div className={`overflow-hidden rounded-2xl border ${t.card}`}>
      <div className={`border-b px-4 py-3 text-sm font-semibold ${t.border}`}>{title}</div>
      {items.map((b, i) => (
        <button key={b.secid} onClick={() => openBond(b.secid)}
          className={`flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm transition-colors ${i % 2 ? t.rowEven : t.rowOdd} ${t.rowHover}`}>
          <span className={`w-5 text-xs font-bold ${t.faint}`}>{i + 1}</span>
          <span className="min-w-0 flex-1 truncate font-medium">{b.short_name}</span>
          <span className={`font-semibold tabular-nums ${t.up}`}>{valueOf(b)}</span>
        </button>
      ))}
    </div>
  );

  return (
    <div className="mx-auto max-w-7xl px-4 py-5">
      <h1 className="mb-4 text-xl font-bold tracking-tight">Обзор рынка</h1>
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
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={byType} dataKey="value" nameKey="name" innerRadius={52} outerRadius={80} paddingAngle={3} strokeWidth={0}>
                  {byType.map((e) => <Cell key={e.key} fill={e.hex} />)}
                </Pie>
                <RTooltip contentStyle={{ background: t.tooltipBg, border: `1px solid ${t.grid}`, borderRadius: 10, fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-1 flex flex-col gap-1.5 text-sm">
            {byType.map((e) => (
              <div key={e.key} className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full" style={{ background: e.hex }} />
                <span className={`flex-1 ${t.muted}`}>{e.name}</span>
                <b className="tabular-nums">{e.value}</b>
              </div>
            ))}
          </div>
        </div>
        <TopList title="Топ-5 по доходности" items={topYield} valueOf={(b) => `${fmt(b.yield_at_prev_wa_price)}%`} />
        <TopList title="Топ-5 по купону" items={topCoupon} valueOf={(b) => `${fmt(b.coupon_percent)}%`} />
      </div>
    </div>
  );
}

/* ============================================================
   Страница: Тарифы
   ============================================================ */
function PricingPage({ t, A, go }) {
  const plans = [
    { name: "Бесплатный", price: "0 ₽", period: "навсегда", cta: "Начать бесплатно",
      features: ["Базовые фильтры", "10 результатов на запрос", "Обзор рынка"],
      missing: ["Экспорт в Excel", "Уведомления", "API доступ"] },
    { name: "Про", price: "490 ₽", period: "в месяц", cta: "Оформить Про", popular: true,
      features: ["Все фильтры без ограничений", "Неограниченные результаты", "Экспорт в Excel", "Уведомления о ценах", "Избранное и watchlist"],
      missing: ["API доступ"] },
    { name: "Бизнес", price: "2 990 ₽", period: "в месяц", cta: "Связаться с нами",
      features: ["Всё из тарифа Про", "API доступ", "Массовый экспорт", "Приоритетная поддержка"], missing: [] },
  ];
  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold tracking-tight">Тарифы</h1>
        <p className={`mt-2 text-sm ${t.muted}`}>Начните бесплатно. Переходите на Про, когда понадобится больше.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {plans.map((p) => (
          <div key={p.name} className={`relative flex flex-col rounded-2xl border p-5 ${t.card} ${p.popular ? `border-2 ${A.border}` : ""}`}>
            {p.popular && (
              <span className={`absolute -top-3 left-1/2 flex -translate-x-1/2 items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold ${A.solid}`}>
                <Zap size={11} /> Популярный
              </span>
            )}
            <div className="text-sm font-semibold">{p.name}</div>
            <div className="mt-2 flex items-baseline gap-1.5">
              <span className="text-3xl font-bold tabular-nums">{p.price}</span>
              <span className={`text-xs ${t.faint}`}>{p.period}</span>
            </div>
            <ul className="mt-4 flex flex-1 flex-col gap-2 text-sm">
              {p.features.map((f) => (
                <li key={f} className="flex items-start gap-2">
                  <Check size={15} className={`mt-0.5 shrink-0 ${A.text}`} /> {f}
                </li>
              ))}
              {p.missing.map((f) => (
                <li key={f} className={`flex items-start gap-2 ${t.faint}`}>
                  <X size={15} className="mt-0.5 shrink-0 opacity-50" /> {f}
                </li>
              ))}
            </ul>
            <button onClick={() => go("screener")}
              className={`mt-5 rounded-lg py-2 text-sm font-semibold transition-colors ${p.popular ? A.solid : `border ${t.btn}`}`}>
              {p.cta}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ============================================================
   App: тема + роутинг + общее состояние скринера
   ============================================================ */
export default function App() {
  const [dark, setDark] = useState(true);
  const [accent, setAccent] = useState("emerald");
  const [route, setRoute] = useState("screener"); // screener | dashboard | pricing
  const [selected, setSelected] = useState(null); // secid открытой в панели бумаги

  // Состояние скринера живёт здесь, чтобы сохраняться при навигации
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState({ field: "yield_at_prev_wa_price", order: "desc" });
  const [page, setPage] = useState(1);

  const t = makeTokens(dark);
  const A = { ...ACCENTS[accent][dark ? "dark" : "light"], hex: ACCENTS[accent].hex };
  const go = (r) => setRoute(r);

  return (
    <div className={`min-h-screen transition-colors ${t.page}`} style={{ fontFamily: "'Inter','Manrope',system-ui,sans-serif" }}>
      <Header route={route} go={go} dark={dark} setDark={setDark} accent={accent} setAccent={setAccent} t={t} A={A} />
      {route === "screener" && (
        <ScreenerPage
          st={{ filters, setFilters, search, setSearch, sort, setSort, page, setPage }}
          t={t} A={A} dark={dark} openBond={setSelected} selected={selected} />
      )}
      {route === "dashboard" && <DashboardPage t={t} A={A} openBond={setSelected} />}
      {route === "pricing" && <PricingPage t={t} A={A} go={go} />}
      {selected && (
        <BondDrawer secid={selected} onClose={() => setSelected(null)} onSelect={setSelected}
          t={t} A={A} dark={dark} />
      )}
      <style>{`@keyframes drawerIn{from{transform:translateX(24px);opacity:0}to{transform:none;opacity:1}}.drawer-in{animation:drawerIn .18s ease-out}`}</style>
    </div>
  );
}
