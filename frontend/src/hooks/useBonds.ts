import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { getBond, getBonds, getMarketOverview } from "../api/bonds";
import type { Bond, BondFilterParams } from "../api/types";

export function useBonds(params: BondFilterParams) {
  return useQuery({
    queryKey: ["bonds", params],
    queryFn: () => getBonds(params),
    placeholderData: keepPreviousData, // старые данные видны, пока грузятся новые
    staleTime: 60_000,
  });
}

export function useBond(secid: string | null) {
  return useQuery({
    queryKey: ["bond", secid],
    queryFn: () => getBond(secid!),
    enabled: !!secid,
    staleTime: 60_000,
  });
}

/** Похожие бумаги: тот же тип, доходность в окне ±2.5 п.п. */
export function useSimilarBonds(bond: Bond | undefined) {
  const y = bond?.yield_at_prev_wa_price;
  return useQuery({
    queryKey: ["similar", bond?.secid],
    queryFn: async () => {
      const res = await getBonds({
        security_type: (bond!.security_type as string) ?? undefined,
        yield_min: y != null ? Math.max(0, y - 2.5) : undefined,
        yield_max: y != null ? y + 2.5 : undefined,
        per_page: 6,
        sort_by: "yield_at_prev_wa_price",
        sort_order: "desc",
      });
      return res.items.filter((b) => b.secid !== bond!.secid).slice(0, 5);
    },
    enabled: !!bond,
    staleTime: 60_000,
  });
}

export function useMarketOverview() {
  return useQuery({
    queryKey: ["market-overview"],
    queryFn: getMarketOverview,
    staleTime: 60_000,
  });
}
