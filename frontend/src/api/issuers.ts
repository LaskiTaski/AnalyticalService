import { api } from "./client";
import type { Issuer, IssuerEventsResponse } from "./types";

export async function getIssuer(inn: string): Promise<Issuer> {
  const { data } = await api.get<Issuer>(`/api/v1/issuers/${encodeURIComponent(inn)}`);
  return data;
}

export async function getIssuerEvents(inn: string): Promise<IssuerEventsResponse> {
  const { data } = await api.get<IssuerEventsResponse>(
    `/api/v1/issuers/${encodeURIComponent(inn)}/events`,
  );
  return data;
}
