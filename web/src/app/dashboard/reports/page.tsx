"use client";

import { useState } from "react";
import useSWR from "swr";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input, Select } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import {
  INCIDENT_LABELS,
  STATUS_COLORS,
  STATUS_LABELS,
  formatDate,
  formatNumber,
  formatNumberFull,
} from "@/lib/utils";
import { Search, Eye, Phone } from "lucide-react";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

interface Report {
  id: number;
  tracking_id: string;
  incident_type: string;
  status: string;
  description: string;
  location?: string;
  created_at: string;
  is_anonymous: boolean;
  user?: {
    full_name?: string | null;
    username?: string | null;
    phone?: string | null;
    user_type?: string | null;
    faculty?: string | null;
  } | null;
  attachments: { id: number; file_type: string }[];
}

interface ReportsResponse {
  reports: Report[];
  total: number;
  page: number;
  limit: number;
}

export default function ReportsPage() {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("");
  const [type, setType] = useState("");
  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");

  const params = new URLSearchParams({
    page: String(page),
    limit: "20",
    ...(status ? { status } : {}),
    ...(type ? { type } : {}),
    ...(search ? { search } : {}),
  });

  const { data, isLoading } = useSWR<ReportsResponse>(
    `/api/reports?${params}`,
    fetcher
  );

  const totalPages = data ? Math.ceil(data.total / 20) : 1;

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setSearch(searchInput);
    setPage(1);
  }

  return (
    <div className="space-y-5 sm:space-y-6">
      <div>
        <h1 className="text-xl sm:text-2xl font-semibold text-gray-900 dark:text-white tracking-tight">
          Murojaatlar
        </h1>
        <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
          Jami:{" "}
          <span
            className="font-medium text-gray-900 dark:text-white tabular-nums"
            title={formatNumberFull(data?.total ?? 0)}
          >
            {formatNumber(data?.total ?? 0)}
          </span>{" "}
          ta
        </p>
      </div>

      {/* Filters */}
      <Card className="border-gray-200 shadow-none">
        <CardContent className="p-3 sm:p-4">
          <div className="flex flex-col sm:flex-row sm:flex-wrap gap-2 sm:gap-3 sm:items-center">
            <form onSubmit={handleSearch} className="flex gap-2 flex-1 sm:min-w-[260px]">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  placeholder="F.I.O, telefon, ID, matn..."
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  className="pl-9"
                />
              </div>
              <Button type="submit" size="sm">Qidirish</Button>
            </form>

            <div className="flex gap-2 sm:gap-3">
              <Select
                value={status}
                onChange={(v) => { setStatus(v); setPage(1); }}
                className="flex-1 sm:w-44"
              >
                <option value="">Barcha holatlar</option>
                <option value="NEW">Yangi</option>
                <option value="IN_REVIEW">Ko&apos;rib chiqilmoqda</option>
                <option value="RESOLVED">Hal etildi</option>
                <option value="REJECTED">Rad etildi</option>
              </Select>

              <Select
                value={type}
                onChange={(v) => { setType(v); setPage(1); }}
                className="flex-1 sm:w-44"
              >
                <option value="">Barcha turlar</option>
                <option value="HARASSMENT">Shilqimlik</option>
                <option value="PRESSURE">Tazyiq</option>
                <option value="VIOLENCE">Zo&apos;ravonlik</option>
                <option value="DISCRIMINATION">Kamsitish</option>
                <option value="OTHER">Boshqa</option>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Table (desktop) + Cards (mobile) */}
      {isLoading ? (
        <Card className="border-gray-200 shadow-none">
          <CardContent>
            <div className="flex justify-center py-16">
              <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            </div>
          </CardContent>
        </Card>
      ) : (data?.reports ?? []).length === 0 ? (
        <Card className="border-gray-200 shadow-none">
          <CardContent>
            <p className="text-center text-gray-400 dark:text-gray-500 py-16 text-sm">
              Murojaatlar topilmadi
            </p>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Desktop table */}
          <Card className="hidden md:block border-gray-200 shadow-none">
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-100 dark:border-gray-800 text-left text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                      <th className="px-4 lg:px-6 py-3 font-medium">Tracking ID</th>
                      <th className="px-4 lg:px-6 py-3 font-medium">Tur</th>
                      <th className="px-4 lg:px-6 py-3 font-medium">Holat</th>
                      <th className="px-4 lg:px-6 py-3 font-medium hidden lg:table-cell">Tavsif</th>
                      <th className="px-4 lg:px-6 py-3 font-medium">Murojaatchi</th>
                      <th className="px-4 lg:px-6 py-3 font-medium hidden xl:table-cell">Telefon</th>
                      <th className="px-4 lg:px-6 py-3 font-medium">Sana</th>
                      <th className="px-4 lg:px-6 py-3 font-medium w-12"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50 dark:divide-gray-800">
                    {(data?.reports ?? []).map((r) => (
                      <tr key={r.id} className="hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-colors">
                        <td className="px-4 lg:px-6 py-3 font-mono text-blue-700 dark:text-blue-400 text-xs whitespace-nowrap">
                          {r.tracking_id}
                        </td>
                        <td className="px-4 lg:px-6 py-3 text-gray-700 dark:text-gray-300">
                          {INCIDENT_LABELS[r.incident_type] ?? r.incident_type}
                        </td>
                        <td className="px-4 lg:px-6 py-3">
                          <Badge className={STATUS_COLORS[r.status]}>
                            {STATUS_LABELS[r.status] ?? r.status}
                          </Badge>
                        </td>
                        <td className="px-4 lg:px-6 py-3 max-w-xs hidden lg:table-cell">
                          <p className="truncate text-gray-600 dark:text-gray-400">{r.description}</p>
                        </td>
                        <td className="px-4 lg:px-6 py-3">
                          <p className="text-gray-700 dark:text-gray-300 truncate max-w-[160px]">
                            {r.user?.full_name ?? r.user?.username ?? "—"}
                          </p>
                          {r.user?.faculty && (
                            <p className="text-gray-400 dark:text-gray-500 text-xs">
                              {r.user.faculty.replace(/_/g, " ")}
                            </p>
                          )}
                        </td>
                        <td className="px-4 lg:px-6 py-3 hidden xl:table-cell">
                          {r.user?.phone ? (
                            <span className="flex items-center gap-1 text-gray-600 dark:text-gray-300 font-mono text-xs">
                              <Phone className="w-3 h-3 text-gray-400" />
                              {r.user.phone}
                            </span>
                          ) : (
                            <span className="text-gray-400 dark:text-gray-500 text-xs">—</span>
                          )}
                        </td>
                        <td className="px-4 lg:px-6 py-3 text-gray-400 dark:text-gray-500 text-xs whitespace-nowrap">
                          {formatDate(r.created_at)}
                        </td>
                        <td className="px-4 lg:px-6 py-3">
                          <Link href={`/dashboard/reports/${r.id}`}>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <Eye className="w-4 h-4" />
                            </Button>
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Mobile card list */}
          <div className="md:hidden space-y-2">
            {(data?.reports ?? []).map((r) => (
              <Link
                key={r.id}
                href={`/dashboard/reports/${r.id}`}
                className="block"
              >
                <Card className="border-gray-200 shadow-none hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-colors">
                  <CardContent className="p-4 space-y-2">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0 flex-1">
                        <p className="font-mono text-blue-700 text-xs">{r.tracking_id}</p>
                        <p className="text-gray-700 dark:text-gray-300 text-sm font-medium mt-0.5">
                          {INCIDENT_LABELS[r.incident_type] ?? r.incident_type}
                        </p>
                      </div>
                      <Badge className={STATUS_COLORS[r.status]}>
                        {STATUS_LABELS[r.status] ?? r.status}
                      </Badge>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2">{r.description}</p>
                    <div className="flex items-center justify-between pt-1 text-xs">
                      <span className="text-gray-700 dark:text-gray-300 truncate">
                        {r.user?.full_name ?? r.user?.username ?? "—"}
                      </span>
                      <span className="text-gray-400 dark:text-gray-500 whitespace-nowrap ml-2">
                        {formatDate(r.created_at, "dd.MM.yyyy")}
                      </span>
                    </div>
                    {r.user?.phone && (
                      <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 font-mono">
                        <Phone className="w-3 h-3 text-gray-400" />
                        {r.user.phone}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Sahifa <span className="font-medium text-gray-900">{page}</span> / {totalPages}
          </p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              Oldingi
            </Button>
            <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
              Keyingi
            </Button>
          </div>
        </div>
      )}

      {/* Yoqubjon — Super admin credit */}
      <div className="flex items-center gap-2 text-xs text-gray-400 dark:text-gray-500 pt-2">
        <div className="w-5 h-5 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center text-white text-[10px] font-bold">
          Y
        </div>
        <span>
          Murojaatlar tizimi —{" "}
          <span className="font-medium text-purple-600 dark:text-purple-400">Yoqubjon</span>{" "}
          (Super admin) tomonidan boshqariladi
        </span>
      </div>
    </div>
  );
}
