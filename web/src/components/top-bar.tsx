"use client";

import { usePathname } from "next/navigation";
import { ThemeToggle } from "@/components/theme-toggle";
import { NotificationBell } from "@/components/notification-bell";

const PAGE_TITLES: Record<string, string> = {
  "/dashboard":               "Dashboard",
  "/dashboard/reports":       "Murojaatlar",
  "/dashboard/users":         "Foydalanuvchilar",
  "/dashboard/admins":        "Adminlar",
  "/dashboard/notifications": "Bildirishnomalar",
  "/dashboard/settings":      "Sozlamalar",
};

function getPageTitle(pathname: string): string {
  // /dashboard/reports/123 -> Murojaatlar
  if (pathname.startsWith("/dashboard/reports/") && pathname !== "/dashboard/reports") {
    return "Murojaat tafsilotlari";
  }
  return PAGE_TITLES[pathname] ?? "Dashboard";
}

export function TopBar() {
  const pathname = usePathname();
  const title = getPageTitle(pathname);

  return (
    <header className="hidden lg:flex sticky top-0 z-20 h-14 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800 items-center justify-between px-6">
      <h2 className="text-sm font-medium text-gray-700 dark:text-gray-300">{title}</h2>
      <div className="flex items-center gap-2">
        <NotificationBell />
        <ThemeToggle />
      </div>
    </header>
  );
}
