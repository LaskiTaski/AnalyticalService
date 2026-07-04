import { useQuery } from "@tanstack/react-query";
import { getIssuer, getIssuerEvents } from "../api/issuers";

/** Карточка эмитента (название, ИНН, счётчики). inn = null → запрос не идёт. */
export function useIssuer(inn: string | null | undefined) {
  return useQuery({
    queryKey: ["issuer", inn],
    queryFn: () => getIssuer(inn!),
    enabled: !!inn,
    staleTime: 5 * 60_000, // данные эмитента меняются редко
  });
}

/** Лента риск-событий эмитента, новые сверху. */
export function useIssuerEvents(inn: string | null | undefined) {
  return useQuery({
    queryKey: ["issuer-events", inn],
    queryFn: () => getIssuerEvents(inn!),
    enabled: !!inn,
    staleTime: 5 * 60_000,
  });
}
