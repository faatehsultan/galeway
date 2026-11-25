import { createRootRoute, Outlet } from "@tanstack/react-router";

import { ErrorBoundary } from "@/app/ErrorBoundary";
import { AppHeader } from "@/features/system/AppHeader";
import { NotFound } from "@/features/system/NotFound";

export const Route = createRootRoute({
  component: RootLayout,
  notFoundComponent: NotFound,
  errorComponent: ErrorBoundary,
});

function RootLayout() {
  return (
    <div className="flex min-h-dvh flex-col">
      <a
        href="#main"
        className="sr-only rounded-lg bg-panel px-3 py-2 shadow-float focus:not-sr-only focus:fixed focus:top-3 focus:left-4 focus:z-50"
      >
        Skip to content
      </a>
      <AppHeader />
      <main id="main" className="flex flex-1 flex-col">
        <Outlet />
      </main>
    </div>
  );
}
