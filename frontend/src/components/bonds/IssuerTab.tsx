import { AlertTriangle, ArrowDownRight, ArrowUpRight, Building2, ExternalLink, ShieldCheck } from "lucide-react";
import type { Bond, Issuer, IssuerEvent } from "../../api/types";
import type { AccentStyle, Tokens } from "../../lib/theme";
import { fmtDate } from "../../lib/utils";

interface Props {
  bond: Bond;
  issuer: Issuer | undefined;
  events: IssuerEvent[];
  loading: boolean;
  t: Tokens;
  A: AccentStyle;
  dark: boolean;
}

/** Метаданные типов риск-событий: подпись + степень тяжести для окраски. */
const EVENT_META: Record<string, { label: string; severe: boolean; up?: boolean }> = {
  default: { label: "Дефолт", severe: true },
  tech_default: { label: "Техдефолт", severe: true },
  bankruptcy_intent: { label: "Намерение банкротства", severe: true },
  restructuring: { label: "Реструктуризация", severe: true },
  listing_downgrade: { label: "Понижение листинга", severe: false },
  listing_upgrade: { label: "Повышение листинга", severe: false, up: true },
  state_support_request: { label: "Запрос господдержки", severe: false },
  offer: { label: "Оферта", severe: false },
};

const SOURCE_LABEL: Record<string, string> = {
  moex: "MOEX",
  acra: "АКРА",
  raexpert: "Эксперт РА",
  "e-disclosure": "e-disclosure",
  fedresurs: "Федресурс",
};

function EventBadge({ type, dark }: { type: string; dark: boolean }) {
  const meta = EVENT_META[type] ?? { label: type, severe: false };
  const cls = meta.severe
    ? dark ? "bg-red-950 text-red-400" : "bg-red-100 text-red-700"
    : meta.up
      ? dark ? "bg-emerald-950 text-emerald-400" : "bg-emerald-100 text-emerald-700"
      : dark ? "bg-amber-950 text-amber-400" : "bg-amber-100 text-amber-700";
  const Icon = meta.severe ? AlertTriangle : meta.up ? ArrowUpRight : ArrowDownRight;
  return (
    <span className={`flex shrink-0 items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium ${cls}`}>
      <Icon size={10} /> {meta.label}
    </span>
  );
}

export function IssuerTab({ bond, issuer, events, loading, t, A, dark }: Props) {
  // ИНН ещё не обогащён коллектором (свежая бумага / ОФЗ без ИНН в ISS)
  if (!bond.issuer_inn) {
    return (
      <div className={`rounded-xl border px-3.5 py-6 text-center text-sm ${t.card} ${t.muted}`}>
        <Building2 size={18} className="mx-auto mb-2 opacity-50" />
        Данные об эмитенте пока не собраны.
        <p className={`mt-1 text-[11px] ${t.faint}`}>
          ИНН подтягивается из MOEX ISS в фоне — загляните позже.
        </p>
      </div>
    );
  }

  const issuerRows: [string, string][] = [
    ["ИНН", bond.issuer_inn],
    ...(issuer?.okpo ? ([["ОКПО", issuer.okpo]] as [string, string][]) : []),
    ...(issuer?.ogrn ? ([["ОГРН", issuer.ogrn]] as [string, string][]) : []),
    ["Бумаг в скринере", String(issuer?.bonds_count ?? "—")],
  ];

  return (
    <>
      {/* Карточка эмитента */}
      <div className={`mb-3 overflow-hidden rounded-xl border ${t.card}`}>
        <div className={`flex items-center gap-2 border-b px-3.5 py-2.5 ${t.border}`}>
          <Building2 size={14} className={A.text} />
          <span className="min-w-0 truncate text-sm font-semibold">
            {issuer?.name ?? bond.short_name ?? bond.issuer_inn}
          </span>
        </div>
        {issuerRows.map(([k, v], i) => (
          <div key={k}
            className={`flex items-baseline justify-between gap-4 px-3.5 py-2 ${
              i < issuerRows.length - 1 ? `border-b ${t.border}` : ""}`}>
            <span className={`text-sm ${t.muted}`}>{k}</span>
            <span className="text-right text-sm font-medium tabular-nums">{v}</span>
          </div>
        ))}
      </div>

      {/* Лента риск-событий */}
      <div className={`overflow-hidden rounded-xl border ${t.card}`}>
        <div className={`flex items-center justify-between border-b px-3.5 py-2.5 ${t.border}`}>
          <span className="text-sm font-semibold">Риск-события</span>
          {events.length > 0 && (
            <span className={`text-[11px] ${t.faint}`}>{events.length}</span>
          )}
        </div>

        {loading && <p className={`px-3.5 py-6 text-center text-sm ${t.muted}`}>Загрузка…</p>}

        {!loading && events.length === 0 && (
          <div className={`px-3.5 py-6 text-center text-sm ${t.muted}`}>
            <ShieldCheck size={18} className="mx-auto mb-2 opacity-50" />
            Событий не зафиксировано
            <p className={`mt-1 text-[11px] ${t.faint}`}>
              Отслеживаем: уровень листинга MOEX; скоро — рейтинги, сущфакты, банкротства.
            </p>
          </div>
        )}

        {events.map((e, i) => (
          <div key={e.id}
            className={`px-3.5 py-2.5 ${i % 2 ? t.rowEven : t.rowOdd}`}>
            <div className="flex items-center justify-between gap-2">
              <EventBadge type={e.type} dark={dark} />
              <span className={`shrink-0 text-[11px] tabular-nums ${t.faint}`}>{fmtDate(e.date)}</span>
            </div>
            <p className="mt-1.5 text-sm leading-snug">{e.title}</p>
            <div className={`mt-1 flex items-center gap-2 text-[11px] ${t.faint}`}>
              <span>{SOURCE_LABEL[e.source] ?? e.source}</span>
              {e.url && (
                <a href={e.url} target="_blank" rel="noopener noreferrer"
                  className={`flex items-center gap-0.5 underline underline-offset-2 ${A.text}`}>
                  первоисточник <ExternalLink size={9} />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>

      <p className={`px-1 pt-2 text-[11px] leading-snug ${t.faint}`}>
        Сигналы носят информационный характер и не являются инвестиционной рекомендацией.
        Проверяйте первоисточники.
      </p>
    </>
  );
}
