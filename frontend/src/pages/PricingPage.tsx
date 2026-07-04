import { Check, X, Zap } from "lucide-react";
import { useNavigate } from "react-router-dom";
import type { AccentStyle, Tokens } from "../lib/theme";

interface Props {
  t: Tokens;
  A: AccentStyle;
}

const PLANS = [
  {
    name: "Бесплатный", price: "0 ₽", period: "навсегда", cta: "Начать бесплатно",
    features: ["Базовые фильтры", "10 результатов на запрос", "Обзор рынка"],
    missing: ["Экспорт в Excel", "Уведомления", "API доступ"],
  },
  {
    name: "Про", price: "490 ₽", period: "в месяц", cta: "Оформить Про", popular: true,
    features: ["Все фильтры без ограничений", "Неограниченные результаты", "Экспорт в Excel", "Уведомления о ценах", "Избранное и watchlist"],
    missing: ["API доступ"],
  },
  {
    name: "Бизнес", price: "2 990 ₽", period: "в месяц", cta: "Связаться с нами",
    features: ["Всё из тарифа Про", "API доступ", "Массовый экспорт", "Приоритетная поддержка"],
    missing: [],
  },
];

export function PricingPage({ t, A }: Props) {
  const navigate = useNavigate();
  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold tracking-tight">Тарифы</h1>
        <p className={`mt-2 text-sm ${t.muted}`}>Начните бесплатно. Переходите на Про, когда понадобится больше.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {PLANS.map((p) => (
          <div key={p.name}
            className={`relative flex flex-col rounded-2xl border p-5 ${t.card} ${p.popular ? `border-2 ${A.border}` : ""}`}>
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
            <button onClick={() => navigate("/screener")}
              className={`mt-5 rounded-lg py-2 text-sm font-semibold transition-colors ${p.popular ? A.solid : `border ${t.btn}`}`}>
              {p.cta}
            </button>
          </div>
        ))}
      </div>
      <p className={`mt-6 text-center text-xs ${t.faint}`}>
        Оплата и подписки появятся после запуска авторизации — сейчас все функции открыты.
      </p>
    </div>
  );
}
