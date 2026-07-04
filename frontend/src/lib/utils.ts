import { Building2, Landmark, MapPin, type LucideIcon } from "lucide-react";

/** Форматирование чисел/дат — порт из docs/DesignSystem.jsx. */

export const fmt = (n: number | null | undefined, d = 2): string =>
  n == null ? "—" : n.toLocaleString("ru-RU", { minimumFractionDigits: d, maximumFractionDigits: d });

export const fmtInt = (n: number | null | undefined): string =>
  n == null ? "—" : n.toLocaleString("ru-RU");

export const fmtDate = (iso: string | null | undefined): string => {
  if (!iso) return "—";
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? "—"
    : d.toLocaleDateString("ru-RU", { day: "2-digit", month: "2-digit", year: "numeric" });
};

export const fmtVol = (v: number | null | undefined): string => {
  if (v == null) return "—";
  if (v >= 1e9) return `${(v / 1e9).toLocaleString("ru-RU", { maximumFractionDigits: 1 })} млрд`;
  if (v >= 1e6) return `${(v / 1e6).toLocaleString("ru-RU", { maximumFractionDigits: 1 })} млн`;
  return `${(v / 1e3).toLocaleString("ru-RU", { maximumFractionDigits: 0 })} тыс`;
};

export const plural = (n: number, one: string, few: string, many: string): string => {
  const m10 = n % 10, m100 = n % 100;
  if (m10 === 1 && m100 !== 11) return one;
  if (m10 >= 2 && m10 <= 4 && (m100 < 10 || m100 >= 20)) return few;
  return many;
};

export interface TypeMeta {
  label: string;
  full: string;
  Icon: LucideIcon;
  hex: string;
}

export const TYPE_META: Record<string, TypeMeta> = {
  ofz: { label: "ОФЗ", full: "Государственные (ОФЗ)", Icon: Landmark, hex: "#0ea5e9" },
  corp: { label: "Корп.", full: "Корпоративные", Icon: Building2, hex: "#10b981" },
  muni: { label: "Муни.", full: "Муниципальные", Icon: MapPin, hex: "#f59e0b" },
};

export const typeMeta = (t: string | null | undefined): TypeMeta =>
  TYPE_META[t ?? ""] ?? { label: t ?? "—", full: t ?? "—", Icon: Building2, hex: "#71717a" };

/** График купонных выплат по данным облигации (period + mat_date). */
export function couponSchedule(matDate: string | null, couponPeriod: number | null): Date[] {
  if (!matDate) return [];
  const mat = new Date(matDate);
  if (Number.isNaN(mat.getTime())) return [];
  const step = couponPeriod && couponPeriod > 0 ? couponPeriod : 182;
  const res: Date[] = [];
  let d = new Date();
  for (let i = 0; i < 9; i++) {
    d = new Date(d.getTime() + step * 864e5);
    if (d >= mat) break;
    res.push(new Date(d));
  }
  res.push(mat);
  return res;
}

/* ── Аватары эмитентов ─────────────────────────────────────────────── */

/**
 * База имени эмитента: часть до цифр/номера выпуска,
 * чтобы «РЖД-30 обл» и «РЖД-32 обл» получали один цвет и монограмму.
 */
export function issuerBase(name: string | null | undefined, secid: string): string {
  const n = (name ?? secid).replace(/["«»']/g, "").trim();
  const m = n.match(/^[^\d]+/);
  const base = (m ? m[0] : n).replace(/[\s\-–—._/]+$/g, "").trim();
  return base || n || secid;
}

/** Детерминированный оттенок (0–359) из строки. */
export function hashHue(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (Math.imul(h, 31) + s.charCodeAt(i)) | 0;
  return Math.abs(h) % 360;
}

/** Монограмма: первые 1–2 буквы первого слова («РЖД» → «РЖ», «Сбер» → «СБ»). */
export function monogram(base: string): string {
  const word = base.split(/\s+/)[0] ?? "";
  const letters = word.replace(/[^A-Za-zА-Яа-яЁё]/g, "");
  return (letters.slice(0, 2) || word.slice(0, 2) || "•").toUpperCase();
}
