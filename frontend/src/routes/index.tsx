import { createFileRoute } from "@tanstack/react-router";

import { ApiStatus } from "@/features/system/ApiStatus";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
  return (
    <div className="flex flex-1 items-center justify-center bg-map px-4 py-10">
      <section className="w-full max-w-[496px] rounded-xl border border-border bg-panel p-7 shadow-float">
        <h1 className="font-display text-hero font-bold tracking-[-0.02em]">
          Pick the safest way through the weather.
        </h1>
        <p className="mt-3 text-muted">
          Galeway is under construction. Trip planning is not available yet.
        </p>
        <div className="mt-5 border-t border-border pt-4">
          <ApiStatus />
        </div>
      </section>
    </div>
  );
}
