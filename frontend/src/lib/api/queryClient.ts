import { QueryClient } from "@tanstack/react-query";

import { HttpError } from "./client";

/** CACHING §1: retry network errors and 5xx twice, never 4xx (the request itself is wrong). */
export function shouldRetry(failureCount: number, error: unknown): boolean {
  if (error instanceof HttpError && error.status < 500) return false;
  return failureCount < 2;
}

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: { queries: { retry: shouldRetry, refetchOnWindowFocus: false } },
  });
}
