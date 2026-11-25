import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import type { ComponentProps } from "react";

import { cn } from "@/lib/utils";

// DESIGN §6: primary (accent), secondary (panel + border), ghost. 44 px forms, 36 px toolbars.
export const buttonVariants = cva(
  "inline-flex shrink-0 items-center justify-center gap-2 rounded-lg font-medium whitespace-nowrap transition-colors duration-120 ease-out disabled:pointer-events-none disabled:opacity-50 [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        primary: "bg-accent text-on-accent hover:brightness-110",
        secondary: "border border-border bg-panel text-text hover:bg-sub",
        ghost: "text-muted hover:bg-sub hover:text-text",
      },
      size: {
        default: "h-11 px-4",
        sm: "h-9 rounded-md px-3",
        // 44 px touch target on small screens, 36 px in toolbars.
        icon: "size-11 md:size-9",
      },
    },
    defaultVariants: { variant: "primary", size: "default" },
  },
);

type ButtonProps = ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & { asChild?: boolean };

export function Button({ className, variant, size, asChild = false, ...props }: ButtonProps) {
  const Component = asChild ? Slot : "button";
  return <Component className={cn(buttonVariants({ variant, size }), className)} {...props} />;
}
