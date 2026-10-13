import * as React from "react"
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export type ShimmerButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement>;

export function ShimmerButton({ children, className, ...props }: ShimmerButtonProps) {
  return (
    <button
      className={cn(
        "relative overflow-hidden px-6 py-3 rounded-lg font-medium shadow-lg transition-shadow duration-300 group",
        "bg-white text-black dark:bg-zinc-100 dark:text-zinc-900",
        className
      )}
      {...props}
    >
      <span className="relative z-10 flex items-center justify-center gap-2">{children}</span>
      <div
        className={cn(
          "absolute inset-0 -translate-x-full",
          "bg-gradient-to-r from-transparent via-black/10 dark:via-white/20 to-transparent",
          "group-hover:translate-x-full transition-transform duration-700 ease-in-out"
        )}
      />
    </button>
  )
}