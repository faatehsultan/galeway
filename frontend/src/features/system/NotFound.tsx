import { Link } from "@tanstack/react-router";

import { buttonVariants } from "@/components/ui/button";

export function NotFound() {
  return (
    <div className="mx-auto flex max-w-md flex-col items-start gap-3 px-4 py-16">
      <h1 className="font-display text-h1 font-bold tracking-[-0.02em]">
        This road doesn&rsquo;t go anywhere
      </h1>
      <p className="text-muted">We couldn&rsquo;t find that page. The link may be broken or old.</p>
      <Link to="/" className={buttonVariants()}>
        Plan a trip
      </Link>
    </div>
  );
}
