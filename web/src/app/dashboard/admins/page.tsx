"use client";

import { useState } from "react";
import useSWR, { mutate } from "swr";
import { useSession } from "next-auth/react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate, ROLE_LABELS } from "@/lib/utils";
import { Plus, Loader2, X, Trash2, Power, Crown } from "lucide-react";
import { toast } from "sonner";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

// Loyiha asoschilari — UI da ham qulflanadi (server bilan mos)
const FOUNDER_USERNAMES = new Set(["admin", "yoqubjon"]);
const isFounderUsername = (u: string) => FOUNDER_USERNAMES.has(u.toLowerCase());

interface AdminUser {
  id: number;
  username: string;
  full_name: string;
  role: string;
  is_active: boolean;
  last_login?: string;
  created_at: string;
}

export default function AdminsPage() {
  const { data: session } = useSession();
  const myRole = (session?.user as { role?: string })?.role ?? "";
  const myId = session?.user?.id;
  const isSuperAdmin = myRole === "admin";

  const { data, isLoading } = useSWR<{ admins: AdminUser[] }>("/api/admins", fetcher);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ username: "", full_name: "", password: "", role: "commission" });
  const [saving, setSaving] = useState(false);
  const [busy, setBusy] = useState<number | null>(null);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    const res = await fetch("/api/admins", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    setSaving(false);
    if (res.ok) {
      toast.success("Admin yaratildi");
      setShowForm(false);
      setForm({ username: "", full_name: "", password: "", role: "commission" });
      mutate("/api/admins");
    } else {
      const err = await res.json() as { error: string };
      toast.error(err.error ?? "Xato");
    }
  }

  async function toggleActive(a: AdminUser) {
    if (busy) return;
    setBusy(a.id);
    try {
      const res = await fetch(`/api/admins/${a.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: !a.is_active }),
      });
      if (res.ok) {
        toast.success(a.is_active ? "Nofaol qilindi" : "Faollashtirildi");
        mutate("/api/admins");
      } else {
        const err = (await res.json()) as { error?: string };
        toast.error(err.error ?? "Xato");
      }
    } finally {
      setBusy(null);
    }
  }

  async function deleteAdmin(a: AdminUser) {
    if (busy) return;
    if (!window.confirm(`"${a.full_name}" adminni o'chirishni tasdiqlaysizmi?`)) return;
    setBusy(a.id);
    try {
      const res = await fetch(`/api/admins/${a.id}`, { method: "DELETE" });
      if (res.ok) {
        toast.success("Admin o'chirildi");
        mutate("/api/admins");
      } else {
        const err = (await res.json()) as { error?: string };
        toast.error(err.error ?? "Xato");
      }
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="space-y-5 sm:space-y-6 max-w-5xl">
      <div className="flex items-start sm:items-center justify-between gap-3 flex-col sm:flex-row">
        <div>
          <h1 className="text-xl sm:text-2xl font-semibold text-gray-900 dark:text-white tracking-tight">Adminlar</h1>
          <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Web panel foydalanuvchilari</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)} className="w-full sm:w-auto">
          <Plus className="w-4 h-4 mr-2" />
          Yangi admin
        </Button>
      </div>

      {showForm && (
        <Card className="border-gray-200 shadow-none">
          <CardHeader className="flex-row items-center justify-between pb-3">
            <CardTitle className="text-sm font-medium">Yangi admin qo&apos;shish</CardTitle>
            <button
              onClick={() => setShowForm(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-4 h-4" />
            </button>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label>Foydalanuvchi nomi</Label>
                <Input
                  required
                  value={form.username}
                  onChange={(e) => setForm({ ...form, username: e.target.value })}
                  placeholder="admin2"
                />
              </div>
              <div className="space-y-1.5">
                <Label>To&apos;liq ism</Label>
                <Input
                  required
                  value={form.full_name}
                  onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                  placeholder="Aziz Karimov"
                />
              </div>
              <div className="space-y-1.5">
                <Label>Parol</Label>
                <Input
                  required
                  type="password"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  placeholder="••••••••"
                  minLength={8}
                />
              </div>
              <div className="space-y-1.5">
                <Label>Rol</Label>
                <select
                  value={form.role}
                  onChange={(e) => setForm({ ...form, role: e.target.value })}
                  className="flex h-9 w-full rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {["commission", "psychologist", "legal", "admin"].map((r) => (
                    <option key={r} value={r}>{ROLE_LABELS[r]}</option>
                  ))}
                </select>
              </div>
              <div className="md:col-span-2 flex gap-2 pt-2">
                <Button type="submit" disabled={saving}>
                  {saving && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  Saqlash
                </Button>
                <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                  Bekor qilish
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <Card className="border-gray-200 shadow-none">
          <CardContent>
            <div className="flex justify-center py-16">
              <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            </div>
          </CardContent>
        </Card>
      ) : (data?.admins ?? []).length === 0 ? (
        <Card className="border-gray-200 shadow-none">
          <CardContent>
            <p className="text-center text-gray-400 dark:text-gray-500 py-16 text-sm">Adminlar yo&apos;q</p>
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
                      <th className="px-4 lg:px-6 py-3 font-medium">Admin</th>
                      <th className="px-4 lg:px-6 py-3 font-medium">Rol</th>
                      <th className="px-4 lg:px-6 py-3 font-medium">Holat</th>
                      <th className="px-4 lg:px-6 py-3 font-medium hidden lg:table-cell">So&apos;nggi kirish</th>
                      <th className="px-4 lg:px-6 py-3 font-medium hidden xl:table-cell">Yaratilgan</th>
                      {isSuperAdmin && <th className="px-4 lg:px-6 py-3 font-medium text-right">Amal</th>}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50 dark:divide-gray-800">
                    {(data?.admins ?? []).map((a) => {
                      const isMe = String(a.id) === String(myId);
                      const isFounder = isFounderUsername(a.username);
                      // Founder'ga faqat o'zi tegisha oladi
                      const locked = isFounder && !isMe;
                      return (
                      <tr key={a.id} className={`hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-colors ${isFounder ? "bg-gradient-to-r from-purple-50/40 to-transparent dark:from-purple-950/20" : ""}`}>
                        <td className="px-4 lg:px-6 py-3">
                          <div className="flex items-center gap-3">
                            <div className={`w-8 h-8 rounded-full ${isFounder ? "bg-gradient-to-br from-yellow-400 via-purple-500 to-blue-600 ring-2 ring-yellow-300 dark:ring-yellow-500" : "bg-gradient-to-br from-purple-500 to-purple-700"} flex items-center justify-center text-white text-xs font-medium relative`}>
                              {a.full_name[0]?.toUpperCase()}
                              {isFounder && <Crown className="absolute -top-2 -right-1 w-3.5 h-3.5 text-yellow-500 fill-yellow-400 drop-shadow" />}
                            </div>
                            <div>
                              <p className="font-medium text-gray-900 dark:text-white flex items-center gap-1.5">
                                {a.full_name}
                                {isMe && <span className="text-xs text-blue-600">(siz)</span>}
                                {isFounder && (
                                  <Badge className="bg-gradient-to-r from-yellow-400 to-orange-400 text-white text-[10px] px-1.5 py-0 h-4 font-bold uppercase tracking-wide shadow-sm">
                                    Asoschi
                                  </Badge>
                                )}
                              </p>
                              <p className="text-gray-400 dark:text-gray-500 dark:text-gray-400 text-xs">@{a.username}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 lg:px-6 py-3">
                          <Badge variant="secondary">{ROLE_LABELS[a.role] ?? a.role}</Badge>
                        </td>
                        <td className="px-4 lg:px-6 py-3">
                          <Badge className={a.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}>
                            {a.is_active ? "Faol" : "Nofaol"}
                          </Badge>
                        </td>
                        <td className="px-4 lg:px-6 py-3 text-gray-500 dark:text-gray-400 text-xs hidden lg:table-cell">
                          {a.last_login ? formatDate(a.last_login) : "—"}
                        </td>
                        <td className="px-4 lg:px-6 py-3 text-gray-400 dark:text-gray-500 dark:text-gray-400 text-xs hidden xl:table-cell">
                          {formatDate(a.created_at, "dd.MM.yyyy")}
                        </td>
                        {isSuperAdmin && (
                          <td className="px-4 lg:px-6 py-3 text-right whitespace-nowrap">
                            {locked ? (
                              <span
                                className="inline-flex items-center gap-1 text-xs text-purple-600 dark:text-purple-400 font-medium"
                                title="Asoschini o'zgartirish/o'chirib bo'lmaydi"
                              >
                                <Crown className="w-3.5 h-3.5" />
                                Qulflangan
                              </span>
                            ) : (
                              <>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8"
                                  disabled={busy === a.id || isMe}
                                  title={a.is_active ? "Nofaol qilish" : "Faollashtirish"}
                                  onClick={() => toggleActive(a)}
                                >
                                  {busy === a.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Power className="w-4 h-4" />}
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-50"
                                  disabled={busy === a.id || isMe || isFounder}
                                  title={isMe ? "O'zingizni o'chira olmaysiz" : "O'chirish"}
                                  onClick={() => deleteAdmin(a)}
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </>
                            )}
                          </td>
                        )}
                      </tr>
                    );
                    })}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Mobile cards */}
          <div className="md:hidden space-y-2">
            {(data?.admins ?? []).map((a) => {
              const isMe = String(a.id) === String(myId);
              const isFounder = isFounderUsername(a.username);
              const locked = isFounder && !isMe;
              return (
              <Card
                key={a.id}
                className={`border-gray-200 shadow-none ${isFounder ? "bg-gradient-to-r from-purple-50/50 to-transparent dark:from-purple-950/30 border-purple-200 dark:border-purple-900/50" : ""}`}
              >
                <CardContent className="p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <div className={`w-10 h-10 rounded-full ${isFounder ? "bg-gradient-to-br from-yellow-400 via-purple-500 to-blue-600 ring-2 ring-yellow-300 dark:ring-yellow-500" : "bg-gradient-to-br from-purple-500 to-purple-700"} flex items-center justify-center text-white text-sm font-medium flex-shrink-0 relative`}>
                      {a.full_name[0]?.toUpperCase()}
                      {isFounder && <Crown className="absolute -top-2 -right-1 w-4 h-4 text-yellow-500 fill-yellow-400 drop-shadow" />}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="font-medium text-gray-900 dark:text-white truncate flex items-center gap-1.5 flex-wrap">
                        {a.full_name}
                        {isMe && <span className="text-xs text-blue-600">(siz)</span>}
                        {isFounder && (
                          <Badge className="bg-gradient-to-r from-yellow-400 to-orange-400 text-white text-[10px] px-1.5 py-0 h-4 font-bold uppercase tracking-wide shadow-sm">
                            Asoschi
                          </Badge>
                        )}
                      </p>
                      <p className="text-gray-400 dark:text-gray-500 text-xs truncate">@{a.username}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-wrap mb-2">
                    <Badge variant="secondary">{ROLE_LABELS[a.role] ?? a.role}</Badge>
                    <Badge className={a.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}>
                      {a.is_active ? "Faol" : "Nofaol"}
                    </Badge>
                  </div>
                  <div className="text-xs text-gray-400 space-y-0.5">
                    <p>So&apos;nggi: {a.last_login ? formatDate(a.last_login) : "—"}</p>
                    <p>Yaratilgan: {formatDate(a.created_at, "dd.MM.yyyy")}</p>
                  </div>
                  {isSuperAdmin && !locked && (
                    <div className="flex gap-2 pt-3 mt-2 border-t border-gray-100 dark:border-gray-800">
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1"
                        disabled={busy === a.id || isMe}
                        onClick={() => toggleActive(a)}
                      >
                        {busy === a.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Power className="w-4 h-4 mr-1" />}
                        {a.is_active ? "Nofaol" : "Faol"}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-red-600 hover:bg-red-50 border-red-200"
                        disabled={busy === a.id || isMe || isFounder}
                        onClick={() => deleteAdmin(a)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  )}
                  {locked && (
                    <div className="pt-3 mt-2 border-t border-purple-100 dark:border-purple-900/50">
                      <p className="text-xs text-purple-700 dark:text-purple-300 flex items-center gap-1.5 font-medium">
                        <Crown className="w-3.5 h-3.5" />
                        Loyiha asoschisi — qulflangan
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
            })}
          </div>
        </>
      )}
    </div>
  );
}
