import { Monitor, Moon, Sun } from "lucide-react";

import { useTheme } from "@/app/ThemeProvider";
import { NEXT_PREFERENCE, type ThemePreference } from "@/app/theme";
import { Button } from "@/components/ui/button";

const ICONS = { system: Monitor, light: Sun, dark: Moon } satisfies Record<
  ThemePreference,
  unknown
>;

/** Cycles System → Light → Dark. The label always says what is set and what a click does. */
export function ThemeToggle() {
  const { preference, setPreference } = useTheme();
  const next = NEXT_PREFERENCE[preference];
  const Icon = ICONS[preference];

  return (
    <Button
      variant="secondary"
      size="icon"
      className="bg-sub"
      aria-label={`Theme: ${preference}. Switch to ${next}.`}
      onClick={() => {
        setPreference(next);
      }}
    >
      <Icon aria-hidden="true" />
    </Button>
  );
}
