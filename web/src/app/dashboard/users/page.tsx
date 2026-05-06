"use client";

import { useState } from "react";
import useSWR, { mutate } from "swr";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import {
  formatDate,
  FACULTY_LABELS,
  USER_TYPE_LABELS,
  formatNumber,
  formatNumberFull,
} from "@/lib/utils";
import { Search, FileText, Phone, Ban, CheckCircle2, Loader2 } from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

interface TgUser {
  id: number;
  telegram_id: string;
  phone?: string | null;
  full_name?: string | null;
  username?: string | null;
  user_type?: string | null;
  faculty?: string | null;
  course?: number | null;
  direction?: string | null;
  group_name?: string | null;
  position?: string | null;
  is_registered: boolean;
  registered_at?: string | null;
  language: string;
  role: string;
  is_blocked: boolean;
  created_at: string;
  _count: { reports: number };
}

export default function UsersPage() {
  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");

  const params = new URLSearchParams({
    page: String(page),
    limit: "20",
    ...(search ? { search } : {}),
  });
  const queryKey = `/api/users?${params}`;
  const { data, isLoading } = useSWR<{ users: TgUser[]; total: number }>(
    queryKey,
    fetcher,
  );

  const totalPages = data ? Math.ceil(data.total / 20) : 1;
  const [busy, setBusy] = useState<number | null>(null);

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setSearch(searchInput);
    setPage(1);
  }

  async function toggleBlock(u: TgUser) {
    if (busy) return;
    const action = u.is_blocked ? "blokdan chiqarishni" : "bloklashni";
    if (!window.confirm(`"${u.full_name ?? u.username ?? "foydalanuvchi"}" ni ${action} tasdiqlaysizmi?`)) return;
    setBusy(u.id);
    try {
      const res = await fetch(`/api/users/${u.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_blocked: !u.is_blocked }),
      });
      if (res.ok) {
        toast.success(u.is_blocked ? "Blokdan chiqarildi" : "Bloklandi");
        mutate(queryKey);
      } else {
        const err = (await res.json()) as { error?: string };
        toast.error(err.error ?? "Xato");
      }
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="space-y-5 sm:space-y-6">
      <div>
        <h1 className="text-xl sm:text-2xl font-semibold text-gray-900 dark:text-white tracking-tight">
          Foydalanuvchilar
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

      <Card className="border-gray-200 dark:border-gray-800 shadow-none">
        <CardContent className="p-3 sm:p-4">
          <form onSubmit={handleSearch} className="flex gap-2 max-w-md">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500" />
              <Input
                placeholder="F.I.O, telefon, username..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="pl-9"
              />
            </div>
            <Button type="submit" size="sm">
              Qidirish
            </Button>
          </form>
        </CardContent>
      </Card>

      {isLoading ? (
        <Card className="border-gray-200 dark:border-gray-800 shadow-none">
          <CardContent>
            <div className="flex justify-center py-16">
              <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            </div>
          </CardContent>
        </Card>
      ) : (data?.users ?? []).length === 0 ? (
        <Card className="border-gray-200 dark:border-gray-800 shadow-none">
          <CardContent>
            <p className="text-center text-gray-400 dark:text-gray-500 py-16 text-sm">
              Foydalanuvchilar topilmadi
            </p>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Desktop table */}
          <Card className="hidden md:block border-gray-200 dark:border-gray-800 shadow-none">
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-100 dark:border-gray-800 text-left text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                      <th className="px-4 lg:px-6 py-3 font-medium">Foydalanuvchi</th>
                      <th className="px-4 lg:px-6 py-3 font-medium">Telefon</th>
                      <th className="px-4 lg:px-6 py-3 font-medium">Maqom</th>
                      <th className="px-4 lg:px-6 py-3 font-medium hidden lg:table-cell">
                        Fakultet / Yo&apos;nalish
                      </th>
                      <th className="px-4 lg:px-6 py-3 font-medium text-center">Murojaatlar</th>
                      <th className="px-4 lg:px-6 py-3 font-medium">Holat</th>
                      <th className="px-4 lg:px-6 py-3 font-medium hidden xl:table-cell">Sana</th>
                      <th className="px-4 lg:px-6 py-3 font-medium text-right">Amal</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50 dark:divide-gray-800">
                    {(data?.users ?? []).map((u) => (
                      <tr
                        key={u.id}
                        className="hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-colors"
                      >
                        <td className="px-4 lg:px-6 py-3">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white text-xs font-medium flex-shrink-0">
                              {(u.full_name ?? u.username ?? "?")[0]?.toUpperCase()}
                            </div>
                            <div className="min-w-0">
                              <p className="font-medium text-gray-900 dark:text-white truncate">
                                {u.full_name ?? "—"}
                              </p>
                              <p className="text-gray-400 dark:text-gray-500 text-xs truncate">
                                {u.username ? `@${u.username}` : `ID ${u.telegram_id}`}
                              </p>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 lg:px-6 py-3">
                          {u.phone ? (
                            <span className="flex items-center gap-1 font-mono text-xs text-gray-700 dark:text-gray-300">
                              <Phone className="w-3 h-3 text-gray-400 dark:text-gray-500" />
                              {u.phone}
                            </span>
                          ) : (
                            <span className="text-gray-400 dark:text-gray-500 text-xs">—</span>
                          )}
                        </td>
                        <td className="px-4 lg:px-6 py-3">
                          {u.user_type ? (
                            <Badge variant="secondary">
                              {USER_TYPE_LABELS[u.user_type] ?? u.user_type}
                            </Badge>
                          ) : (
                            <span className="text-gray-400 dark:text-gray-500 text-xs">—</span>
                          )}
                        </td>
                        <td className="px-4 lg:px-6 py-3 text-xs hidden lg:table-cell">
                          {u.faculty && (
                            <p className="text-gray-700 dark:text-gray-300">
                              {FACULTY_LABELS[u.faculty] ?? u.faculty}
                            </p>
                          )}
                          {u.direction && (
                            <p className="text-gray-500 dark:text-gray-400">
                              {u.direction}
                              {u.course && ` · ${u.course}-kurs`}
                              {u.group_name && ` · ${u.group_name}`}
                            </p>
                          )}
                          {u.position && (
                            <p className="text-gray-500 dark:text-gray-400">{u.position}</p>
                          )}
                          {!u.faculty && !u.direction && !u.position && (
                            <span className="text-gray-400 dark:text-gray-500">—</span>
                          )}
                        </td>
                        <td className="px-4 lg:px-6 py-3 text-center">
                          {u._count.reports > 0 ? (
                            <Link
                              href="/dashboard/reports"
                              className="inline-flex items-center gap-1 text-blue-600 dark:text-blue-400 hover:underline font-medium"
                            >
                              <FileText className="w-3.5 h-3.5" />
                              {u._count.reports}
                            </Link>
                          ) : (
                            <span className="text-gray-400 dark:text-gray-500">0</span>
                          )}
                        </td>
                        <td className="px-4 lg:px-6 py-3">
                          {u.is_blocked ? (
                            <Badge className="bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300">
                              Bloklangan
                            </Badge>
                          ) : u.is_registered ? (
                            <Badge className="bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300">
                              Faol
                            </Badge>
                          ) : (
                            <Badge className="bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300">
                              Yangi
                            </Badge>
                          )}
                        </td>
                        <td className="px-4 lg:px-6 py-3 text-gray-400 dark:text-gray-500 text-xs whitespace-nowrap hidden xl:table-cell">
                          {formatDate(u.created_at, "dd.MM.yyyy")}
                        </td>
                        <td className="px-4 lg:px-6 py-3 text-right whitespace-nowrap">
                          <Button
                            variant="ghost"
                            size="icon"
                            className={u.is_blocked ? "h-8 w-8 text-green-600 hover:bg-green-50" : "h-8 w-8 text-red-600 hover:bg-red-50"}
                            disabled={busy === u.id}
                            title={u.is_blocked ? "Blokdan chiqarish" : "Bloklash"}
                            onClick={() => toggleBlock(u)}
                          >
                            {busy === u.id ? <Loader2 className="w-4 h-4 animate-spin" /> : u.is_blocked ? <CheckCircle2 className="w-4 h-4" /> : <Ban className="w-4 h-4" />}
                          </Button>
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
            {(data?.users ?? []).map((u) => (
              <Card key={u.id} className="border-gray-200 dark:border-gray-800 shadow-none">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white text-sm font-medium flex-shrink-0">
                      {(u.full_name ?? u.username ?? "?")[0]?.toUpperCase()}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="font-medium text-gray-900 dark:text-white truncate">
                        {u.full_name ?? "—"}
                      </p>
                      <p className="text-gray-400 dark:text-gray-500 text-xs truncate">
                        {u.username ? `@${u.username}` : `ID ${u.telegram_id}`}
                      </p>
                    </div>
                    {u.is_blocked ? (
                      <Badge className="bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300">
                        Bloklangan
                      </Badge>
                    ) : u.is_registered ? (
                      <Badge className="bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300">
                        Faol
                      </Badge>
                    ) : (
                      <Badge className="bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300">
                        Yangi
                      </Badge>
                    )}
                  </div>
                  <div className="space-y-1.5 text-xs">
                    {u.phone && (
                      <div className="flex items-center gap-1.5 text-gray-700 dark:text-gray-300 font-mono">
                        <Phone className="w-3 h-3 text-gray-400 dark:text-gray-500" />
                        {u.phone}
                      </div>
                    )}
                    {u.user_type && (
                      <p className="text-gray-600 dark:text-gray-400">
                        <span className="text-gray-400 dark:text-gray-500">Maqom:</span>{" "}
                        {USER_TYPE_LABELS[u.user_type] ?? u.user_type}
                      </p>
                    )}
                    {u.faculty && (
                      <p className="text-gray-600 dark:text-gray-400">
                        <span className="text-gray-400 dark:text-gray-500">Fakultet:</span>{" "}
                        {FACULTY_LABELS[u.faculty] ?? u.faculty}
                      </p>
                    )}
                    {u.direction && (
                      <p className="text-gray-500 dark:text-gray-400">
                        {u.direction}
                        {u.course && ` · ${u.course}-kurs`}
                        {u.group_name && ` · ${u.group_name}`}
                      </p>
                    )}
                    {u.position && (
                      <p className="text-gray-500 dark:text-gray-400">{u.position}</p>
                    )}
                    <div className="flex items-center justify-between pt-1.5 border-t border-gray-100 dark:border-gray-800 mt-2">
                      {u._count.reports > 0 ? (
                        <Link
                          href="/dashboard/reports"
                          className="inline-flex items-center gap-1 text-blue-600 dark:text-blue-400 hover:underline font-medium"
                        >
                          <FileText className="w-3.5 h-3.5" />
                          {u._count.reports} ta murojaat
                        </Link>
                      ) : (
                        <span className="text-gray-400 dark:text-gray-500">Murojaat yo&apos;q</span>
                      )}
                      <span className="text-gray-400 dark:text-gray-500">
                        {formatDate(u.created_at, "dd.MM.yyyy")}
                      </span>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      className={u.is_blocked
                        ? "w-full mt-2 text-green-700 border-green-200 hover:bg-green-50"
                        : "w-full mt-2 text-red-700 border-red-200 hover:bg-red-50"}
                      disabled={busy === u.id}
                      onClick={() => toggleBlock(u)}
                    >
                      {busy === u.id ? (
                        <Loader2 className="w-4 h-4 mr-1.5 animate-spin" />
                      ) : u.is_blocked ? (
                        <CheckCircle2 className="w-4 h-4 mr-1.5" />
                      ) : (
                        <Ban className="w-4 h-4 mr-1.5" />
                      )}
                      {u.is_blocked ? "Blokdan chiqarish" : "Bloklash"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Sahifa <span className="font-medium text-gray-900 dark:text-white">{page}</span> / {totalPages}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
            >
              Oldingi
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              Keyingi
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
