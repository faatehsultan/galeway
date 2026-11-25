import { RouterProvider, createMemoryHistory } from "@tanstack/react-router";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { Providers } from "./providers";
import { createAppRouter } from "./router";

async function renderAt(path: string) {
  const router = createAppRouter(createMemoryHistory({ initialEntries: [path] }));
  render(
    <Providers>
      <RouterProvider router={router} />
    </Providers>,
  );
  await router.load();
}

describe("app shell", () => {
  it("renders the home page with a header, a single h1 and a skip link", async () => {
    await renderAt("/");

    expect(await screen.findByRole("heading", { level: 1 })).toHaveTextContent(
      "Pick the safest way through the weather.",
    );
    expect(screen.getByRole("link", { name: "Galeway" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Skip to content" })).toHaveAttribute("href", "#main");
    expect(await screen.findByText(/API online/)).toBeInTheDocument();
  });

  it("shows a designed 404 for an unknown path", async () => {
    await renderAt("/no-such-page");

    expect(await screen.findByRole("heading", { level: 1 })).toHaveTextContent(
      "This road doesn’t go anywhere",
    );
    expect(screen.getByRole("link", { name: "Plan a trip" })).toHaveAttribute("href", "/");
  });

  it("cycles the theme, applies it and remembers the choice", async () => {
    await renderAt("/");
    const user = userEvent.setup();

    await user.click(await screen.findByRole("button", { name: /Theme: system/ }));
    expect(document.documentElement).toHaveAttribute("data-theme", "light");
    expect(localStorage.getItem("galeway.theme")).toBe("light");

    await user.click(screen.getByRole("button", { name: /Theme: light/ }));
    expect(document.documentElement).toHaveAttribute("data-theme", "dark");
    expect(localStorage.getItem("galeway.theme")).toBe("dark");

    await user.click(screen.getByRole("button", { name: /Theme: dark/ }));
    expect(localStorage.getItem("galeway.theme")).toBe("system");
  });
});
