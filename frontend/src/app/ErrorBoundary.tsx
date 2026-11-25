import { Button } from "@/components/ui/button";

/** Render-crash fallback. Never shows the raw error to the user (golden rule 8). */
export function ErrorBoundary() {
  return (
    <div role="alert" className="mx-auto flex max-w-md flex-col items-start gap-3 px-4 py-16">
      <h1 className="font-display text-h1 font-bold tracking-[-0.02em]">Something went wrong</h1>
      <p className="text-muted">
        Galeway hit an unexpected problem. Reloading usually fixes it, and your trip is still in the
        address bar.
      </p>
      <Button
        onClick={() => {
          window.location.reload();
        }}
      >
        Reload
      </Button>
    </div>
  );
}
