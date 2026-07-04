/** Типы соответствуют Pydantic-схемам бэкенда (src/api/schemas.py). */

export type SecurityType = "ofz" | "corp" | "muni";

export interface Bond {
  id: number;
  secid: string;
  isin: string | null;
  short_name: string | null;
  full_name: string | null;
  board_id: string | null;

  prev_price: number | null;
  face_value: number | null;
  accrued_int: number | null;
  lot_size: number | null;

  yield_at_prev_wa_price: number | null;
  coupon_percent: number | null;
  coupon_value: number | null;
  coupon_period: number | null;
  coupon_frequency: number | null;

  mat_date: string | null; // ISO date
  offer_date: string | null;
  days_to_maturity: number | null;

  list_level: number | null;
  qualified_only: boolean | null;
  security_type: SecurityType | string | null;

  duration: number | null;
  volume_today: number | null;

  /** Риск-сигналы эмитента (этап 1) */
  issuer_inn: string | null;
  risk_events_count: number;
  has_severe_events: boolean;

  updated_at: string;
}

export interface BondListResponse {
  items: Bond[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface MarketOverview {
  total_bonds: number;
  by_type: Record<string, number>;
  by_board: Record<string, number>;
  avg_yield: number | null;
  avg_coupon: number | null;
  avg_duration: number | null;
  last_updated: string | null;
}

/** Query-параметры GET /api/v1/bonds. */
export interface BondFilterParams {
  page?: number;
  per_page?: number;
  price_min?: number;
  price_max?: number;
  yield_min?: number;
  yield_max?: number;
  coupon_min?: number;
  coupon_max?: number;
  coupon_frequency?: number;
  days_min?: number;
  days_max?: number;
  qualified?: boolean;
  list_level_max?: number;
  security_type?: string; // csv: "corp,muni"
  board_id?: string;
  search?: string;
  risk_only?: boolean;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

/** ── Риск-сигналы эмитента ─────────────────────────────────── */

export type IssuerEventType =
  | "default"
  | "tech_default"
  | "bankruptcy_intent"
  | "listing_downgrade"
  | "listing_upgrade"
  | "state_support_request"
  | "offer"
  | "restructuring";

export interface IssuerEvent {
  id: number;
  inn: string;
  type: IssuerEventType | string;
  date: string; // ISO date
  title: string;
  url: string | null;
  source: string;
  secid: string | null;
}

export interface Issuer {
  inn: string;
  name: string | null;
  ogrn: string | null;
  okpo: string | null;
  bonds_count: number;
  events_count: number;
}

export interface IssuerEventsResponse {
  inn: string;
  items: IssuerEvent[];
  total: number;
}
