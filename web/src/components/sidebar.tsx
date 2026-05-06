"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { signOut, useSession } from "next-auth/react";
import { cn, ROLE_LABELS } from "@/lib/utils";
import { ThemeToggle } from "@/components/theme-toggle";
import { NotificationBell } from "@/components/notification-bell";
import {
  LayoutDashboard,
  FileText,
  Users,
  Settings,
  LogOut,
  Bell,
  UserCog,
  Menu,
  X,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/reports", label: "Murojaatlar", icon: FileText },
  { href: "/dashboard/users", label: "Foydalanuvchilar", icon: Users },
  { href: "/dashboard/admins", label: "Adminlar", icon: UserCog },
  { href: "/dashboard/notifications", label: "Bildirishnomalar", icon: Bell },
  { href: "/dashboard/settings", label: "Sozlamalar", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { data: session } = useSession();
  const [open, setOpen] = useState(false);
  const role = (session?.user as { role?: string })?.role ?? "";
  const initial = session?.user?.name?.[0]?.toUpperCase() ?? "A";

  // Sahifa o'zgarsa drawer'ni yopamiz
  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  // ESC bossa drawer yopiladi
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const sidebarContent = (
    <>
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-gray-100 dark:border-gray-800">
        <div className="relative w-10 h-10 rounded-full overflow-hidden flex-shrink-0 ring-2 ring-blue-100 dark:ring-blue-900">
          <Image
            src="/logo.jpg"
            alt="TDTU Termiz filiali logo"
            fill
            sizes="40px"
            className="object-cover"
            priority
          />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-gray-900 dark:text-white font-semibold text-sm leading-tight">Himoya</p>
          <p className="text-gray-400 dark:text-gray-500 text-xs mt-0.5 truncate">TDTU Termiz filiali</p>
        </div>
        {/* Mobile close button */}
        <button
          onClick={() => setOpen(false)}
          className="lg:hidden text-gray-400 hover:text-gray-600 dark:hover:text-white -m-1 p-1"
          aria-label="Yopish"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active =
            href === "/dashboard"
              ? pathname === href
              : pathname.startsWith(href);

          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all",
                active
                  ? "bg-blue-50 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300"
                  : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800/50 hover:text-gray-900 dark:hover:text-white"
              )}
            >
              <Icon
                className={cn(
                  "w-4 h-4 flex-shrink-0",
                  active && "text-blue-600 dark:text-blue-400"
                )}
                strokeWidth={active ? 2.5 : 2}
              />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Profile + Sign out */}
      <div className="border-t border-gray-100 dark:border-gray-800 p-3 space-y-1">
        {session?.user && (
          <div className="flex items-center gap-3 px-3 py-2 mb-1">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white text-sm font-semibold flex-shrink-0">
              {initial}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                {session.user.name}
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-500 truncate">
                {ROLE_LABELS[role] ?? role}
              </p>
            </div>
          </div>
        )}
        <button
          onClick={() => signOut({ callbackUrl: "/login" })}
          className="flex items-center gap-3 px-3 py-2.5 w-full rounded-lg text-sm font-medium text-gray-600 dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-950/30 hover:text-red-600 dark:hover:text-red-400 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Chiqish
        </button>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile top bar */}
      <header className="lg:hidden sticky top-0 z-30 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 flex items-center gap-3 px-4 h-14">
        <button
          onClick={() => setOpen(true)}
          className="text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white p-1.5 -ml-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
          aria-label="Menyu"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="flex items-center gap-2 min-w-0 flex-1">
          <div className="relative w-7 h-7 rounded-full overflow-hidden flex-shrink-0 ring-1 ring-blue-100 dark:ring-blue-900">
            <Image
              src="/logo.jpg"
              alt="Logo"
              fill
              sizes="28px"
              className="object-cover"
            />
          </div>
          <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">Himoya</p>
        </div>
        <NotificationBell />
        <ThemeToggle />
      </header>

      {/* Backdrop (mobile only) */}
      {open && (
        <div
          onClick={() => setOpen(false)}
          className="lg:hidden fixed inset-0 z-40 bg-gray-900/50 backdrop-blur-sm transition-opacity"
        />
      )}

      {/* Desktop sidebar */}
      <aside className="hidden lg:flex lg:w-64 lg:flex-col lg:min-h-screen lg:border-r lg:border-gray-200 dark:lg:border-gray-800 bg-white dark:bg-gray-900">
        {sidebarContent}
      </aside>

      {/* Mobile drawer */}
      <aside
        className={cn(
          "lg:hidden fixed top-0 bottom-0 left-0 z-50 w-72 max-w-[85vw] bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col transition-transform duration-200 ease-out",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {sidebarContent}
      </aside>
    </>
  );
}
