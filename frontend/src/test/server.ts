import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

export const API = "http://localhost:8000";

export const healthOk = http.get(`${API}/api/v1/health`, () =>
  HttpResponse.json({ status: "ok", version: "abcdef1234567" }),
);

/** Recorded-style handlers only: tests never reach a real provider (golden rule 4). */
export const server = setupServer(healthOk);
