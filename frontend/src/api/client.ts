import axios from "axios";

/**
 * Пустой baseURL = same-origin: в dev запросы уходят через Vite-прокси,
 * в Docker — через nginx, который проксирует /api на сервис api.
 */
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "",
  timeout: 15_000,
});
