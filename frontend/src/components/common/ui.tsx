import React from "react";
import { ChevronDown, ChevronLeft, ChevronRight } from "lucide-react";
import type { AccentStyle, Tokens } from "../../lib/theme";
import { hashHue, issuerBase, monogram } from "../../lib/utils";

export function FilterSection({ title, badge, open, onToggle, children, t, A }: {
  title: string; badge: number; open: boolean; onToggle: () => void;
  children: React.ReactNode; t: Tokens; A: AccentStyle;
}) {
  return (
    <div className={`border-b last:border-b-0 ${t.border}`}>
      <button onClick={onToggle}
        className={`flex w-full items-center justify-between py-3 text-left text-xs font-semibold uppercase tracking-wider transition-colors ${A.hover}`}>
        <span className="flex items-center gap-2">
          {title}
          {badge > 0 && (
            <span className={`rounded-full px-1.5 py-0.5 text-[10px] font-bold normal-case ${A.soft}`}>{badge}</span>
          )}
        </span>
        <ChevronDown size={14} className={`transition-transform ${open ? "rotate-180" : ""}`} />
      </button>
      {open && <div className="pb-4">{children}</div>}
    </div>
  );
}

export function RangePair({ minVal, maxVal, onMin, onMax, t, A }: {
  minVal: string; maxVal: string; onMin: (v: string) => void; onMax: (v: string) => void;
  t: Tokens; A: AccentStyle;
}) {
  const cls = `w-full min-w-0 rounded-lg border px-2.5 py-1.5 text-sm outline-none transition-colors ${t.input} ${A.focus}`;
  return (
    <div className="flex gap-2">
      <input type="number" inputMode="decimal" placeholder="от" value={minVal}
        onChange={(e) => onMin(e.target.value)} className={cls} />
      <input type="number" inputMode="decimal" placeholder="до" value={maxVal}
        onChange={(e) => onMax(e.target.value)} className={cls} />
    </div>
  );
}

export function ListLevelBadge({ level, dark }: { level: number | null; dark: boolean }) {
  if (!level || level < 1 || level > 3) return <span>—</span>;
  // Заполненные «таблетки»: 1 — teal (лучший), 2 — олива, 3 — роза
  const p = dark
    ? ["bg-[#17b597] text-[#04231b]", "bg-[#8a8420] text-[#fdfbe8]", "bg-[#c2405c] text-white"]
    : ["bg-[#0f9f78] text-white", "bg-[#9a941f] text-white", "bg-[#c2405c] text-white"];
  return (
    <span className={`inline-flex h-6 min-w-9 items-center justify-center rounded-full px-2 text-xs font-bold ${p[level - 1]}`}>
      {level}
    </span>
  );
}

export function Pagination({ page, pages, onPage, t, A }: {
  page: number; pages: number; onPage: (p: number) => void; t: Tokens; A: AccentStyle;
}) {
  const nums = [...new Set([1, pages, page - 1, page, page + 1])]
    .filter((n) => n >= 1 && n <= pages)
    .sort((a, b) => a - b);
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
      <button onClick={() => onPage(Math.min(pages, page + 1))} disabled={page >= pages} aria-label="Вперёд"
        className={`flex h-8 w-8 items-center justify-center rounded-lg border transition-colors disabled:opacity-30 ${t.btn}`}>
        <ChevronRight size={15} />
      </button>
    </div>
  );
}

/**
 * Аватар эмитента: монограмма на градиенте, цвет — детерминированный хэш
 * базового имени, поэтому выпуски одного эмитента выглядят одинаково,
 * а разные эмитенты различимы с первого взгляда (проблема «стены текста»).
 */
export function IssuerAvatar({ name, secid, size = 32, className = "" }: {
  name: string | null | undefined; secid: string; size?: number; className?: string;
}) {
  const base = issuerBase(name, secid);
  const hue = hashHue(base);
  return (
    <span
      className={`flex shrink-0 select-none items-center justify-center rounded-lg font-display font-extrabold text-white shadow-sm ${className}`}
      style={{
        width: size, height: size,
        fontSize: Math.round(size * 0.36),
        background: `linear-gradient(135deg, hsl(${hue} 58% 48%), hsl(${(hue + 38) % 360} 55% 36%))`,
      }}
      aria-hidden="true">
      {monogram(base)}
    </span>
  );
}
