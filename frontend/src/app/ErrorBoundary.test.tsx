import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ErrorBoundary } from "./ErrorBoundary";

describe("ErrorBoundary", () => {
  it("shows a calm message and a way out, never a raw error", () => {
    render(<ErrorBoundary />);

    expect(screen.getByRole("alert")).toHaveTextContent("Something went wrong");
    expect(screen.getByRole("button", { name: "Reload" })).toBeInTheDocument();
  });
});
