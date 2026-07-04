import { api } from "./client";
import type { Bond, BondFilterParams, BondListResponse, MarketOverview } from "./types";

export async function getBonds(params: BondFilterParams): Promise<BondListResponse> {
  const { data } = await api.get<BondListResponse>("/api/v1/bonds", { params });
  return data;
}

export async function getBond(secid: string): Promise<Bond> {
  const { data } = await api.get<Bond>(`/api/v1/bonds/${encodeURIComponent(secid)}`);
  return data;
}

export async function getMarketOverview(): Promise<MarketOverview> {
  const { data } = await api.get<MarketOverview>("/api/v1/stats/market-overview");
  return data;
}
