import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { format } from "date-fns";
import { uz } from "date-fns/locale";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** BigInt qiymatlarini string ga aylantirib JSON qaytaradi */
export function jsonResponse(data: unknown, status = 200): Response {
  const body = JSON.stringify(data, (_key, val) =>
    typeof val === "bigint" ? val.toString() : val
  );
  return new Response(body, {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

export function formatDate(date: Date | string, fmt = "dd.MM.yyyy HH:mm") {
  return format(new Date(date), fmt, { locale: uz });
}

/** Katta raqamlarni qisqartirish: 1500 → "1.5K", 1_200_000 → "1.2M", 999_000_000 → "999M", 1.5B */
export function formatNumber(n: number): string {
  if (n < 1000) return n.toString();
  if (n < 1_000_000) {
    const v = n / 1000;
    return (v < 10 ? v.toFixed(1) : Math.round(v).toString()) + "K";
  }
  if (n < 1_000_000_000) {
    const v = n / 1_000_000;
    return (v < 10 ? v.toFixed(1) : Math.round(v).toString()) + "M";
  }
  const v = n / 1_000_000_000;
  return (v < 10 ? v.toFixed(1) : Math.round(v).toString()) + "B";
}

/** 1234567 → "1 234 567" (to'liq raqam, bo'sh joy bilan) */
export function formatNumberFull(n: number): string {
  return n.toLocaleString("uz-UZ").replace(/,/g, " ");
}

// DB da UPPERCASE ENUM ishlatiladi (HARASSMENT, NEW, USER, ...)
// Ikkala variant ham qo'llab-quvvatlanadi
export const INCIDENT_LABELS: Record<string, string> = {
  HARASSMENT: "Shilqimlik",
  PRESSURE: "Tazyiq",
  VIOLENCE: "Zo'ravonlik",
  DISCRIMINATION: "Kamsitish",
  OTHER: "Boshqa",
  harassment: "Shilqimlik",
  pressure: "Tazyiq",
  violence: "Zo'ravonlik",
  discrimination: "Kamsitish",
  other: "Boshqa",
};

export const STATUS_LABELS: Record<string, string> = {
  NEW: "Yangi",
  IN_REVIEW: "Ko'rib chiqilmoqda",
  RESOLVED: "Hal etildi",
  REJECTED: "Rad etildi",
  new: "Yangi",
  in_review: "Ko'rib chiqilmoqda",
  resolved: "Hal etildi",
  rejected: "Rad etildi",
};

export const STATUS_COLORS: Record<string, string> = {
  NEW: "bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300",
  IN_REVIEW: "bg-yellow-100 text-yellow-800 dark:bg-yellow-950 dark:text-yellow-300",
  RESOLVED: "bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300",
  REJECTED: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300",
  new: "bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300",
  in_review: "bg-yellow-100 text-yellow-800 dark:bg-yellow-950 dark:text-yellow-300",
  resolved: "bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300",
  rejected: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300",
};

export const ROLE_LABELS: Record<string, string> = {
  USER: "Foydalanuvchi",
  PSYCHOLOGIST: "Psixolog",
  LEGAL: "Huquqiy yordam",
  COMMISSION: "Komissiya a'zosi",
  ADMIN: "Super admin",
  user: "Foydalanuvchi",
  psychologist: "Psixolog",
  legal: "Huquqiy yordam",
  commission: "Komissiya a'zosi",
  admin: "Super admin",
};

export const USER_TYPE_LABELS: Record<string, string> = {
  STUDENT: "Talaba (Bakalavr)",
  MASTER: "Magistrant",
  TEACHER: "O'qituvchi",
  STAFF: "Universitet xodimi",
  OTHER: "Boshqa",
};

export const FACULTY_LABELS: Record<string, string> = {
  DAVOLASH_1: "1-son Davolash fakulteti",
  DAVOLASH_2: "2-son Davolash fakulteti",
  PEDIATRIYA: "Pediatriya fakulteti",
  XALQARO: "Xalqaro ta'lim fakulteti",
};
