"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import useSWR, { mutate } from "swr";
import { Bell, BellOff, Check, ExternalLink, CheckCheck, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { INCIDENT_LABELS, formatDate } from "@/lib/utils";

const fetcher = (url: string) => fetch(url).then((r) => r.json());
const POLL_INTERVAL = 15_000;
const SEEN_KEY = "himoya:lastSeenReportId";

interface ReportItem {
  id: number;
  tracking_id: string;
  incident_type: string;
  status: string;
  created_at: string;
  user?: { full_name?: string | null; username?: string | null } | null;
}

export function NotificationBell() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [permission, setPermission] = useState<NotificationPermission | "unsupported">("default");
  const [lastSeenId, setLastSeenId] = useState<number>(0);
  const [marking, setMarking] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const { data } = useSWR<{ reports: ReportItem[]; total: number }>(
    "/api/reports?limit=10&status=NEW",
    fetcher,
    { refreshInterval: POLL_INTERVAL, revalidateOnFocus: true }
  );

  const reports = data?.reports ?? [];
  // Yangi (ko'rilmagan) — id > lastSeenId
  const unseenCount = reports.filter((r) => r.id > lastSeenId).length;

  useEffect(() => {
    if (typeof window === "undefined" || !("Notification" in window)) {
      setPermission("unsupported");
      return;
    }
    setPermission(Notification.permission);
  }, []);

  // localStorage'dan lastSeenId
  useEffect(() => {
    const stored = localStorage.getItem(SEEN_KEY);
    if (stored) setLastSeenId(parseInt(stored));

    // Boshqa tabda o'zgarsa sync qilish
    const onStorage = (e: StorageEvent) => {
      if (e.key === SEEN_KEY && e.newValue) {
        setLastSeenId(parseInt(e.newValue));
      }
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  // Click outside
  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  // ESC
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  async function requestPermission() {
    if (!("Notification" in window)) return;
    const result = await Notification.requestPermission();
    setPermission(result);
  }

  async function markAllSeen() {
    if (reports.length === 0 || marking) return;
    const ok = window.confirm(
      "Barcha yangi murojaatlar 'Ko'rib chiqilmoqda' holatiga o'tkaziladi. Davom etamizmi?",
    );
    if (!ok) return;

    setMarking(true);
    try {
      const res = await fetch("/api/reports/bulk-mark-read", { method: "POST" });
      if (!res.ok) {
        const err = (await res.json()) as { error?: string };
        toast.error(err.error ?? "Xato");
        return;
      }
      const json = (await res.json()) as { updated: number };
      toast.success(`${json.updated} ta murojaat ko'rildi`);

      const maxId = Math.max(...reports.map((r) => r.id));
      setLastSeenId(maxId);
      localStorage.setItem(SEEN_KEY, String(maxId));
      mutate("/api/reports?limit=10&status=NEW");
      mutate("/api/reports?status=NEW&limit=50");
      mutate("/api/stats");
      setOpen(false);
    } catch (e) {
      toast.error("Xato: " + String(e));
    } finally {
      setMarking(false);
    }
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setOpen((o) => !o)}
        className={cn(
          "relative flex items-center justify-center w-9 h-9 rounded-lg transition-colors",
          "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white",
          "hover:bg-gray-100 dark:hover:bg-gray-800",
          open && "bg-gray-100 dark:bg-gray-800"
        )}
        aria-label="Bildirishnomalar"
      >
        <Bell className="w-4.5 h-4.5" strokeWidth={2} />
        {unseenCount > 0 && (
          <span className="absolute top-1 right-1 flex items-center justify-center min-w-[18px] h-[18px] px-1 rounded-full bg-red-500 text-white text-[10px] font-semibold leading-none animate-pulse">
            {unseenCount > 99 ? "99+" : unseenCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-80 sm:w-96 max-w-[calc(100vw-2rem)] rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-lg z-50 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-800">
            <div className="flex items-center gap-2 min-w-0">
              <Bell className="w-4 h-4 text-blue-600 dark:text-blue-400 flex-shrink-0" />
              <p className="text-sm font-semibold text-gray-900 dark:text-white">
                Bildirishnomalar
              </p>
              {unseenCount > 0 && (
                <span className="text-xs px-1.5 py-0.5 rounded-full bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300 font-medium">
                  {unseenCount} yangi
                </span>
              )}
            </div>
            {reports.length > 0 && (
              <button
                onClick={markAllSeen}
                disabled={marking}
                className="text-xs text-blue-600 dark:text-blue-400 hover:underline inline-flex items-center gap-1 font-medium flex-shrink-0 disabled:opacity-50"
                title="Hammasini ko'rib chiqilmoqda holatiga o'tkazish"
              >
                {marking ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <CheckCheck className="w-3.5 h-3.5" />
                )}
                Hammasi ko&apos;rildi
              </button>
            )}
          </div>

          {/* Permission warning */}
          {permission === "default" && (
            <div className="px-4 py-3 bg-blue-50 dark:bg-blue-950/30 border-b border-blue-100 dark:border-blue-900/50">
              <p className="text-xs text-gray-700 dark:text-gray-300 mb-2">
                Brauzer bildirishnomalarini yoqing — yangi murojaatlar haqida xabar olasiz.
              </p>
              <button
                onClick={requestPermission}
                className="text-xs font-medium text-blue-700 dark:text-blue-400 hover:underline inline-flex items-center gap-1"
              >
                <Check className="w-3 h-3" />
                Yoqish
              </button>
            </div>
          )}

          {/* List */}
          <div className="max-h-[400px] overflow-y-auto">
            {reports.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-10 text-gray-400 dark:text-gray-500">
                <BellOff className="w-7 h-7 mb-2" strokeWidth={1.5} />
                <p className="text-sm">Hozircha yangi xabar yo&apos;q</p>
              </div>
            ) : (
              reports.map((r) => {
                const userName = r.user?.full_name ?? r.user?.username ?? "Anonim";
                const isUnseen = r.id > lastSeenId;
                return (
                  <button
                    key={r.id}
                    onClick={() => {
                      router.push(`/dashboard/reports/${r.id}`);
                      setOpen(false);
                    }}
                    className={cn(
                      "w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800/50 border-b border-gray-50 dark:border-gray-800/50 last:border-b-0 transition-colors relative",
                      isUnseen && "bg-blue-50/40 dark:bg-blue-950/20"
                    )}
                  >
                    {isUnseen && (
                      <span className="absolute left-1.5 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-blue-500" />
                    )}
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 rounded-full bg-blue-50 dark:bg-blue-950/50 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Bell className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          Yangi murojaat
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">
                          {INCIDENT_LABELS[r.incident_type] ?? r.incident_type} — {userName}
                        </p>
                        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1 font-mono">
                          {r.tracking_id} · {formatDate(r.created_at, "dd.MM HH:mm")}
                        </p>
                      </div>
                      <ExternalLink className="w-3.5 h-3.5 text-gray-300 dark:text-gray-600 flex-shrink-0 mt-1" />
                    </div>
                  </button>
                );
              })
            )}
          </div>

          {/* Footer */}
          <div className="px-4 py-2.5 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between">
            <p className="text-xs text-gray-400 dark:text-gray-500">
              {reports.length} ta yangi murojaat
            </p>
            <Link
              href="/dashboard/notifications"
              onClick={() => setOpen(false)}
              className="text-xs text-blue-600 dark:text-blue-400 hover:underline font-medium"
            >
              Hammasini ko&apos;rish →
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
