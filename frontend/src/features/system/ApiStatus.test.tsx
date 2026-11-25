import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { ApiStatus } from "./ApiStatus";

import { API, server } from "@/test/server";

function renderStatus() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={client}>
      <ApiStatus />
    </QueryClientProvider>,
  );
}

describe("ApiStatus", () => {
  it("shows a connecting state first, then the short version when online", async () => {
    renderStatus();

    expect(screen.getByRole("status")).toHaveTextContent("Connecting to the API…");
    expect(await screen.findByText("API online · abcdef1")).toBeInTheDocument();
  });

  it("says the API is unreachable when the health check fails", async () => {
    server.use(http.get(`${API}/api/v1/health`, () => new HttpResponse(null, { status: 500 })));

    renderStatus();

    expect(await screen.findByText("API unreachable")).toBeInTheDocument();
  });
});
