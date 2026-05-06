"use client";

import { useEffect, useRef, useState } from "react";
import useSWR from "swr";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

interface ReportItem {
  id: number;
  tracking_id: string;
  incident_type: string;
  created_at: string;
  user?: { full_name?: string | null; username?: string | null } | null;
}

const POLL_INTERVAL = 15_000; // 15s
const STORAGE_KEY = "himoya:lastSeenReportId";

/**
 * Yangi murojaatlar kelganda toast + browser notification + sound.
 * Layout'ga bir marta o'rnatiladi, hamma sahifalarda ishlaydi.
 */
export function NewReportNotifier() {
  const router = useRouter();
  const [permission, setPermission] = useState<NotificationPermission | "unsupported">("default");
  const lastSeenIdRef = useRef<number | null>(null);
  const initializedRef = useRef(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Browser notification permission
  useEffect(() => {
    if (typeof window === "undefined" || !("Notification" in window)) {
      setPermission("unsupported");
      return;
    }
    setPermission(Notification.permission);
    if (Notification.permission === "default") {
      // Birinchi marta — auto-request qilmaymiz, foydalanuvchi xohlasa Settings'dan beradi
    }
  }, []);

  // Initial value localStorage'dan
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) lastSeenIdRef.current = parseInt(stored);
  }, []);

  const { data } = useSWR<{ reports: ReportItem[]; total: number }>(
    "/api/reports?limit=10&status=NEW",
    fetcher,
    { refreshInterval: POLL_INTERVAL, revalidateOnFocus: true }
  );

  useEffect(() => {
    if (!data?.reports) return;

    // Birinchi yuklanishda — faqat lastSeen'ni o'rnatamiz
    if (!initializedRef.current) {
      initializedRef.current = true;
      const maxId = Math.max(0, ...data.reports.map((r) => r.id));
      if (lastSeenIdRef.current === null) {
        lastSeenIdRef.current = maxId;
        localStorage.setItem(STORAGE_KEY, String(maxId));
      }
      return;
    }

    // Yangi murojaatlarni topamiz
    const newOnes = data.reports.filter(
      (r) => lastSeenIdRef.current !== null && r.id > lastSeenIdRef.current
    );

    if (newOnes.length === 0) return;

    // 1. Toast
    newOnes.slice(0, 3).forEach((r) => {
      const userName = r.user?.full_name ?? r.user?.username ?? "Anonim";
      toast.success("🔔 Yangi murojaat", {
        description: `${userName} — ${r.tracking_id}`,
        duration: 8000,
        action: {
          label: "Ko'rish",
          onClick: () => router.push(`/dashboard/reports/${r.id}`),
        },
      });
    });
    if (newOnes.length > 3) {
      toast.info(`Yana ${newOnes.length - 3} ta yangi murojaat`, {
        action: {
          label: "Hammasi",
          onClick: () => router.push("/dashboard/reports?status=NEW"),
        },
      });
    }

    // 2. Sound
    try {
      audioRef.current?.play().catch(() => {});
    } catch {}

    // 3. Browser notification
    if (permission === "granted" && document.hidden) {
      newOnes.slice(0, 3).forEach((r) => {
        const userName = r.user?.full_name ?? r.user?.username ?? "Anonim";
        const n = new Notification("🔔 Himoya — Yangi murojaat", {
          body: `${userName}\nID: ${r.tracking_id}`,
          icon: "/logo.jpg",
          badge: "/logo.jpg",
          tag: `report-${r.id}`,
          requireInteraction: false,
        });
        n.onclick = () => {
          window.focus();
          router.push(`/dashboard/reports/${r.id}`);
          n.close();
        };
      });
    }

    // 4. Yangilash
    const newMaxId = Math.max(...newOnes.map((r) => r.id));
    lastSeenIdRef.current = newMaxId;
    localStorage.setItem(STORAGE_KEY, String(newMaxId));
  }, [data, permission, router]);

  return (
    <>
      {/* Sound: ding (data URI — kichik beep) */}
      <audio
        ref={audioRef}
        preload="auto"
        src="data:audio/wav;base64,UklGRkIBAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YR4BAAAAAAEAAQACAAEABAACAAYABwAJAAsADQAOABAAEgATABYAFwAYABoAGwAcAB0AHQAeAB4AHwAeAB4AHQAcABwAGgAYABYAEwARAA4ACwAIAAQAAQD8//j/9P/u/+r/5P/g/9z/2P/V/9P/0v/R/9D/0P/Q/9H/0v/V/9j/3P/g/+T/6f/u//L/9//8/wAABAAJAA0AEgAUABcAGgAdAB8AIQAjACUAJgAmACcAJwAnACYAJgAlACQAIgAhAB4AHAAaABcAFAARAA4ACgAGAAMA////AP4A/AD8APsA+wD7APwA/QD+/wAAAQACAAQABwAJAA=="
      />
      {/* permission requestor endi navbar Bell dropdown'da va Settings'da bor */}
    </>
  );
}
