import { useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  Check, CreditCard, LayoutDashboard, Moon, Palette, Sun, Table2,
} from "lucide-react";
import { ACCENTS, type AccentStyle, type Tokens } from "../../lib/theme";
import { LogoMark } from "./Logo";

interface Props {
  dark: boolean;
  setDark: (v: boolean) => void;
  accent: string;
  setAccent: (v: string) => void;
  t: Tokens;
  A: AccentStyle;
}

const NAV = [
  { to: "/screener", label: "Скринер", Icon: Table2 },
  { to: "/dashboard", label: "Дашборд", Icon: LayoutDashboard },
  { to: "/pricing", label: "Тарифы", Icon: CreditCard },
];

export function Header({ dark, setDark, accent, setAccent, t, A }: Props) {
  const [pickerOpen, setPickerOpen] = useState(false);
  const { pathname } = useLocation();
  const pickerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!pickerOpen) return;
    const onDown = (e: MouseEvent) => {
      if (pickerRef.current && !pickerRef.current.contains(e.target as Node)) setPickerOpen(false);
    };
    window.addEventListener("mousedown", onDown);
    return () => window.removeEventListener("mousedown", onDown);
  }, [pickerOpen]);

  return (
    <header className={`sticky top-0 z-30 border-b ${t.header}`}>
      <div className="flex h-14 w-full items-center gap-4 px-4 sm:px-6">
        <Link to="/screener" className="flex items-center gap-2.5">
          <span className={`flex h-8 w-8 items-center justify-center rounded-xl ${A.solid}`}>
            <LogoMark size={18} />
          </span>
          <span className="hidden font-display text-[15px] font-extrabold tracking-tight sm:block">
            Bond Screener
          </span>
        </Link>
        <nav className="flex gap-1 text-sm">
          {NAV.map(({ to, label, Icon }) => (
            <Link key={to} to={to}
              className={`flex items-center gap-1.5 rounded-full px-3.5 py-1.5 transition-colors ${
                pathname.startsWith(to) ? `font-semibold ${A.soft}` : `${t.muted} ${A.hover}`}`}>
              <Icon size={14} /> <span className="hidden md:inline">{label}</span>
            </Link>
          ))}
        </nav>
        <div className="relative ml-auto flex items-center gap-2" ref={pickerRef}>
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
          <button className={`hidden rounded-full border-2 px-4 py-1.5 text-sm font-semibold transition-colors sm:block ${A.border} ${A.text} ${A.hover} hover:bg-white/5`}>
            Войти
          </button>
        </div>
      </div>
    </header>
  );
}
