"use client";

import { useEffect, useState } from "react";
import { useTheme } from "next-themes";
import { Sun, Moon, Monitor } from "lucide-react";
import { cn } from "@/lib/utils";

const OPTIONS = [
  { value: "light",  label: "Yorug'", icon: Sun },
  { value: "dark",   label: "Tungi",  icon: Moon },
  { value: "system", label: "Tizim",  icon: Monitor },
] as const;

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  if (!mounted) {
    return (
      <div className="flex items-center gap-1 p-1 rounded-lg bg-gray-100 dark:bg-gray-800">
        {OPTIONS.map((o) => (
          <div key={o.value} className="w-7 h-7" />
        ))}
      </div>
    );
  }

  return (
    <div
      role="radiogroup"
      aria-label="Mavzu tanlash"
      className="flex items-center gap-0.5 p-0.5 rounded-lg bg-gray-100 dark:bg-gray-800"
    >
      {OPTIONS.map(({ value, label, icon: Icon }) => {
        const active = theme === value;
        return (
          <button
            key={value}
            role="radio"
            aria-checked={active}
            aria-label={label}
            title={label}
            onClick={() => setTheme(value)}
            className={cn(
              "flex items-center justify-center w-7 h-7 rounded-md transition-colors",
              active
                ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm"
                : "text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            )}
          >
            <Icon className="w-3.5 h-3.5" />
          </button>
        );
      })}
    </div>
  );
}
