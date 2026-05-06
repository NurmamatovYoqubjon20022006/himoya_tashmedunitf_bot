"use client";

import { useEffect, useState } from "react";
import useSWR, { mutate } from "swr";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { BellOff, FileText, Clock, CheckCheck, Loader2 } from "lucide-react";
import { toast } from "sonner";
import {
  INCIDENT_LABELS,
  STATUS_COLORS,
  STATUS_LABELS,
  formatDate,
  cn,
} from "@/lib/utils";
import Link from "next/link";

const fetcher = (url: string) => fetch(url).then((r) => r.json());
const SEEN_KEY = "himoya:lastSeenReportId";

interface Report {
  id: number;
  tracking_id: string;
  incident_type: string;
  status: string;
  description: string;
  created_at: string;
  user?: { full_name?: string; username?: string } | null;
}

export default function NotificationsPage() {
  const { data, isLoading } = useSWR<{ reports: Report[]; total: number }>(
    "/api/reports?status=NEW&limit=50",
    fetcher,
    { refreshInterval: 30000 }
  );

  const [lastSeenId, setLastSeenId] = useState<number>(0);

  useEffect(() => {
    const stored = localStorage.getItem(SEEN_KEY);
    if (stored) setLastSeenId(parseInt(stored));
    const onStorage = (e: StorageEvent) => {
      if (e.key === SEEN_KEY && e.newValue) setLastSeenId(parseInt(e.newValue));
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  const reports = data?.reports ?? [];
  const unseenCount = reports.filter((r) => r.id > lastSeenId).length;
  const [marking, setMarking] = useState(false);

  function markLocalSeen(maxId: number) {
    setLastSeenId(maxId);
    localStorage.setItem(SEEN_KEY, String(maxId));
    window.dispatchEvent(new StorageEvent("storage", {
      key: SEEN_KEY,
      newValue: String(maxId),
    }));
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
        toast.error(err.error ?? "Xato yuz berdi");
        return;
      }
      const json = (await res.json()) as { updated: number };
      toast.success(`${json.updated} ta murojaat ko'rildi deb belgilandi`);

      const maxId = Math.max(...reports.map((r) => r.id));
      markLocalSeen(maxId);
      mutate("/api/reports?status=NEW&limit=50");
      mutate("/api/reports?limit=10&status=NEW");
      mutate("/api/stats");
    } catch (e) {
      toast.error("Tarmoqda xato: " + String(e));
    } finally {
      setMarking(false);
    }
  }

  return (
    <div className="space-y-5 sm:space-y-6 max-w-4xl">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="min-w-0">
          <h1 className="text-xl sm:text-2xl font-semibold text-gray-900 dark:text-white tracking-tight">
            Bildirishnomalar
          </h1>
          <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
            Yangi murojaatlar va tizim hodisalari
          </p>
        </div>
        <div className="flex items-center gap-2">
          {unseenCount > 0 && (
            <Badge className="bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300">
              {unseenCount} ko&apos;rilmagan
            </Badge>
          )}
          {reports.length > 0 && (
            <Button
              size="sm"
              variant="outline"
              onClick={markAllSeen}
              disabled={marking}
            >
              {marking ? (
                <Loader2 className="w-4 h-4 mr-1.5 animate-spin" />
              ) : (
                <CheckCheck className="w-4 h-4 mr-1.5" />
              )}
              Hammasi ko&apos;rildi
            </Button>
          )}
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-16">
          <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : reports.length === 0 ? (
        <Card className="border-gray-200 dark:border-gray-800 shadow-none">
          <CardContent className="flex flex-col items-center justify-center py-16">
            <div className="w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-3">
              <BellOff className="w-5 h-5 text-gray-400 dark:text-gray-500" />
            </div>
            <p className="text-gray-700 dark:text-gray-200 font-medium text-sm">
              Hozircha yangi xabar yo&apos;q
            </p>
            <p className="text-gray-400 dark:text-gray-500 text-xs mt-1">
              Yangi murojaatlar avtomatik bu yerda ko&apos;rinadi
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {reports.map((r) => {
            const isUnseen = r.id > lastSeenId;
            return (
              <Link key={r.id} href={`/dashboard/reports/${r.id}`} className="block">
                <Card
                  className={cn(
                    "border-gray-200 dark:border-gray-800 shadow-none transition-colors relative overflow-hidden",
                    "hover:bg-gray-50/50 dark:hover:bg-gray-800/30",
                    isUnseen && "bg-blue-50/30 dark:bg-blue-950/20 border-blue-200 dark:border-blue-900/50"
                  )}
                >
                  {isUnseen && (
                    <span className="absolute left-0 top-0 bottom-0 w-1 bg-blue-500" />
                  )}
                  <CardContent className="p-4 flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-blue-50 dark:bg-blue-950/50 flex items-center justify-center flex-shrink-0">
                      <FileText className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-3 mb-1">
                        <p className="font-medium text-gray-900 dark:text-white text-sm">
                          Yangi murojaat:{" "}
                          <span className="font-mono text-blue-700 dark:text-blue-400">
                            {r.tracking_id}
                          </span>
                          {isUnseen && (
                            <span className="ml-2 inline-block w-1.5 h-1.5 rounded-full bg-blue-500" />
                          )}
                        </p>
                        <Badge className={STATUS_COLORS[r.status]}>
                          {STATUS_LABELS[r.status]}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 truncate mb-1">
                        {INCIDENT_LABELS[r.incident_type] ?? r.incident_type} —{" "}
                        {r.user?.full_name ?? r.user?.username ?? "Anonim"}
                      </p>
                      <p className="text-xs text-gray-400 dark:text-gray-500 truncate mb-1.5">
                        {r.description}
                      </p>
                      <div className="flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
                        <Clock className="w-3 h-3" />
                        {formatDate(r.created_at)}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
