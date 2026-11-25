import { useQuery } from "@tanstack/react-query";

import { getHealth } from "@/lib/api/client";
import { cn } from "@/lib/utils";

/** Shows whether the API answers. Doubles as the cold-start pre-warm (ARCHITECTURE §4). */
export function ApiStatus() {
  const { data, isError } = useQuery({
    queryKey: ["health"],
    queryFn: ({ signal }) => getHealth(signal),
    staleTime: 60_000,
  });

  const text = isError
    ? "API unreachable"
    : data
      ? `API online · ${data.version.slice(0, 7)}`
      : "Connecting to the API…";

  return (
    <p role="status" className="inline-flex items-center gap-2 font-mono text-small text-muted">
      <span
        aria-hidden="true"
        className={cn(
          "size-2 rounded-full",
          isError ? "bg-risk-severe" : data ? "bg-risk-low" : "bg-alt",
        )}
      />
      {text}
    </p>
  );
}
