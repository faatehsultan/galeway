import { Link } from "@tanstack/react-router";

import { ThemeToggle } from "@/features/theme/ThemeToggle";

/** DESIGN §5: 60 px header; §2: mark 30 px, wordmark 19 px Space Grotesk Bold. */
export function AppHeader() {
  return (
    <header className="flex h-[60px] shrink-0 items-center justify-between border-b border-border bg-panel px-5">
      <Link to="/" className="flex items-center gap-2.5 rounded-md text-text no-underline">
        <img src="/galeway-mark.svg" alt="" width={30} height={30} />
        <span className="font-display text-[19px] font-bold tracking-[-0.02em]">Galeway</span>
      </Link>
      <ThemeToggle />
    </header>
  );
}
