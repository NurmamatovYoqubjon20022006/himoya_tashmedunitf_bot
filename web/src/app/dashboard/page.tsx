"use client";

import useSWR from "swr";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { format, parseISO } from "date-fns";
import { uz } from "date-fns/locale";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  INCIDENT_LABELS,
  STATUS_COLORS,
  STATUS_LABELS,
  formatDate,
  formatNumber,
  formatNumberFull,
} from "@/lib/utils";
import {
  FileText,
  Users,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  TrendingUp,
  Inbox,
} from "lucide-react";
import Link from "next/link";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

// Hodisa turlari uchun emoji + rang
const INCIDENT_STYLE: Record<string, { color: string; bg: string; emoji: string }> = {
  HARASSMENT:    { color: "#ef4444", bg: "bg-red-500",     emoji: "🔴" },
  PRESSURE:      { color: "#f59e0b", bg: "bg-amber-500",   emoji: "🟡" },
  VIOLENCE:      { color: "#dc2626", bg: "bg-rose-600",    emoji: "🔥" },
  DISCRIMINATION:{ color: "#8b5cf6", bg: "bg-violet-500",  emoji: "⚖️" },
  OTHER:         { color: "#64748b", bg: "bg-slate-500",   emoji: "📝" },
};

const STATUS_STYLE: Record<string, { color: string; bg: string; label: string; icon: typeof Clock }> = {
  new:        { color: "#3b82f6", bg: "bg-blue-500",   label: "Yangi",              icon: AlertCircle },
  in_review:  { color: "#f59e0b", bg: "bg-amber-500",  label: "Ko'rib chiqilmoqda", icon: Clock },
  resolved:   { color: "#10b981", bg: "bg-emerald-500", label: "Hal etildi",        icon: CheckCircle },
  rejected:   { color: "#ef4444", bg: "bg-red-500",    label: "Rad etildi",         icon: XCircle },
};

interface StatsData {
  stats: {
    total: number;
    new: number;
    in_review: number;
    resolved: number;
    rejected: number;
    users: number;
  };
  recentReports: Array<{
    id: number;
    tracking_id: string;
    incident_type: string;
    status: string;
    created_at: string;
    user?: { full_name?: string; username?: string } | null;
  }>;
  byIncidentType: Array<{ type: string; count: number }>;
  last7Days: Array<{ day: string; count: number }>;
}

export default function DashboardPage() {
  const { data, isLoading } = useSWR<StatsData>("/api/stats", fetcher, {
    refreshInterval: 30000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const stats = data?.stats;

  // Top stat cards
  const statCards = [
    { title: "Jami", value: stats?.total ?? 0, icon: FileText, color: "text-blue-600", bg: "bg-blue-50" },
    { title: "Yangi", value: stats?.new ?? 0, icon: AlertCircle, color: "text-orange-600", bg: "bg-orange-50" },
    { title: "Jarayonda", value: stats?.in_review ?? 0, icon: Clock, color: "text-yellow-600", bg: "bg-yellow-50" },
    { title: "Hal etildi", value: stats?.resolved ?? 0, icon: CheckCircle, color: "text-green-600", bg: "bg-green-50" },
    { title: "Rad etildi", value: stats?.rejected ?? 0, icon: XCircle, color: "text-red-600", bg: "bg-red-50" },
    { title: "Foydalanuvchilar", value: stats?.users ?? 0, icon: Users, color: "text-purple-600", bg: "bg-purple-50" },
  ];

  // Status data
  const statusList = [
    { key: "new",        value: stats?.new ?? 0 },
    { key: "in_review",  value: stats?.in_review ?? 0 },
    { key: "resolved",   value: stats?.resolved ?? 0 },
    { key: "rejected",   value: stats?.rejected ?? 0 },
  ];
  const statusTotal = statusList.reduce((s, x) => s + x.value, 0);

  // Incident data
  const incidentList = (data?.byIncidentType ?? [])
    .map((d) => ({ type: d.type, count: d.count }))
    .sort((a, b) => b.count - a.count);
  const incidentTotal = incidentList.reduce((s, x) => s + x.count, 0);

  // 7 days
  const last7Days = (data?.last7Days ?? []).map((d) => ({
    day: d.day,
    label: format(parseISO(d.day), "d MMM", { locale: uz }),
    count: d.count,
  }));
  const has7DaysData = last7Days.some((d) => d.count > 0);

  return (
    <div className="space-y-5 sm:space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl sm:text-2xl font-semibold text-gray-900 dark:text-white tracking-tight">Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">Tizim umumiy holati</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-3">
        {statCards.map(({ title, value, icon: Icon, color, bg }) => (
          <Card key={title} className="border-gray-200 shadow-none">
            <CardContent className="p-4">
              <div className={`inline-flex p-2 rounded-lg ${bg} mb-3`}>
                <Icon className={`w-4 h-4 ${color}`} />
              </div>
              <p
                className="text-2xl font-semibold text-gray-900 dark:text-white leading-none tabular-nums"
                title={formatNumberFull(value)}
              >
                {formatNumber(value)}
              </p>
              <p className="text-xs text-gray-500 mt-1.5">{title}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Row 1: Last 7 days (big) + Donut */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Area chart */}
        <Card className="lg:col-span-2 border-gray-200 shadow-none">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-blue-50 flex items-center justify-center">
                  <TrendingUp className="w-3.5 h-3.5 text-blue-600" />
                </div>
                <CardTitle className="text-sm font-medium">So&apos;nggi 7 kun</CardTitle>
              </div>
              <span
                className="text-xs text-gray-400"
                title={formatNumberFull(last7Days.reduce((s, d) => s + d.count, 0))}
              >
                {formatNumber(last7Days.reduce((s, d) => s + d.count, 0))} ta murojaat
              </span>
            </div>
          </CardHeader>
          <CardContent>
            {!has7DaysData ? (
              <EmptyChart text="Bu hafta murojaatlar yo'q" />
            ) : (
              <ResponsiveContainer width="100%" height={240}>
                <AreaChart data={last7Days} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                  <defs>
                    <linearGradient id="grad7" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.4} />
                      <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis
                    dataKey="label"
                    tick={{ fontSize: 11, fill: "#94a3b8" }}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 11, fill: "#94a3b8" }}
                    tickLine={false}
                    axisLine={false}
                    allowDecimals={false}
                    width={40}
                    tickFormatter={(v) => formatNumber(v)}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "#fff",
                      border: "1px solid #e2e8f0",
                      borderRadius: 10,
                      fontSize: 12,
                      boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
                    }}
                    labelFormatter={(label, payload) => {
                      const day = payload?.[0]?.payload?.day;
                      return day ? format(parseISO(day), "d MMMM, EEEE", { locale: uz }) : label;
                    }}
                    formatter={(v: number) => [formatNumberFull(v), "Murojaatlar"]}
                  />
                  <Area
                    type="monotone"
                    dataKey="count"
                    stroke="#3b82f6"
                    strokeWidth={2.5}
                    fill="url(#grad7)"
                    dot={{ fill: "#3b82f6", r: 4, strokeWidth: 2, stroke: "#fff" }}
                    activeDot={{ r: 6, strokeWidth: 2, stroke: "#fff" }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Donut — incident types */}
        <Card className="border-gray-200 shadow-none">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Hodisa turlari</CardTitle>
          </CardHeader>
          <CardContent>
            {incidentTotal === 0 ? (
              <EmptyChart text="Murojaatlar yo'q" />
            ) : (
              <div className="relative">
                <ResponsiveContainer width="100%" height={180}>
                  <PieChart>
                    <Pie
                      data={incidentList}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={75}
                      dataKey="count"
                      paddingAngle={3}
                      stroke="none"
                    >
                      {incidentList.map((d) => (
                        <Cell
                          key={d.type}
                          fill={INCIDENT_STYLE[d.type]?.color ?? "#94a3b8"}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        background: "#fff",
                        border: "1px solid #e2e8f0",
                        borderRadius: 10,
                        fontSize: 12,
                        boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
                      }}
                      formatter={(v: number, _n: string, p: { payload?: { type?: string } }) => [
                        formatNumberFull(v),
                        INCIDENT_LABELS[p?.payload?.type ?? ""] ?? "",
                      ]}
                    />
                  </PieChart>
                </ResponsiveContainer>
                {/* Markazda jami soni */}
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <p
                    className="text-2xl font-bold text-gray-900 dark:text-white leading-none tabular-nums"
                    title={formatNumberFull(incidentTotal)}
                  >
                    {formatNumber(incidentTotal)}
                  </p>
                  <p className="text-[10px] text-gray-400 mt-1">Jami</p>
                </div>
              </div>
            )}
            {/* Legend */}
            <div className="mt-3 space-y-1.5">
              {incidentList.map((d) => {
                const pct = incidentTotal ? Math.round((d.count / incidentTotal) * 100) : 0;
                const style = INCIDENT_STYLE[d.type];
                return (
                  <div key={d.type} className="flex items-center gap-2 text-xs">
                    <span
                      className="w-2 h-2 rounded-full flex-shrink-0"
                      style={{ background: style?.color ?? "#94a3b8" }}
                    />
                    <span className="text-gray-700 flex-1 truncate">
                      {INCIDENT_LABELS[d.type] ?? d.type}
                    </span>
                    <span className="text-gray-400 tabular-nums">{pct}%</span>
                    <span
                      className="text-gray-900 font-medium tabular-nums w-12 text-right"
                      title={formatNumberFull(d.count)}
                    >
                      {formatNumber(d.count)}
                    </span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Row 2: Status (horizontal bars) + Incident horizontal bars */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Status horizontal bars */}
        <Card className="border-gray-200 shadow-none">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Holat bo&apos;yicha</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {statusTotal === 0 ? (
              <EmptyChart text="Ma'lumot yo'q" />
            ) : (
              statusList.map(({ key, value }) => {
                const s = STATUS_STYLE[key];
                const pct = statusTotal ? (value / statusTotal) * 100 : 0;
                const Icon = s.icon;
                return (
                  <div key={key}>
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center gap-2 min-w-0">
                        <Icon className="w-3.5 h-3.5 flex-shrink-0" style={{ color: s.color }} />
                        <span className="text-sm text-gray-700 dark:text-gray-200 font-medium truncate">{s.label}</span>
                      </div>
                      <div className="flex items-baseline gap-1.5 flex-shrink-0">
                        <span
                          className="text-sm font-semibold text-gray-900 dark:text-white tabular-nums"
                          title={formatNumberFull(value)}
                        >
                          {formatNumber(value)}
                        </span>
                        <span className="text-xs text-gray-400 tabular-nums">{pct.toFixed(0)}%</span>
                      </div>
                    </div>
                    <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${s.bg}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })
            )}
          </CardContent>
        </Card>

        {/* Incident horizontal bars */}
        <Card className="border-gray-200 shadow-none">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Hodisa turi bo&apos;yicha</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {incidentTotal === 0 ? (
              <EmptyChart text="Ma'lumot yo'q" />
            ) : (
              incidentList.map(({ type, count }) => {
                const s = INCIDENT_STYLE[type];
                const pct = incidentTotal ? (count / incidentTotal) * 100 : 0;
                return (
                  <div key={type}>
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center gap-2 min-w-0">
                        <span
                          className="w-2 h-2 rounded-full flex-shrink-0"
                          style={{ background: s?.color ?? "#94a3b8" }}
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-200 font-medium truncate">
                          {INCIDENT_LABELS[type] ?? type}
                        </span>
                      </div>
                      <div className="flex items-baseline gap-1.5 flex-shrink-0">
                        <span
                          className="text-sm font-semibold text-gray-900 dark:text-white tabular-nums"
                          title={formatNumberFull(count)}
                        >
                          {formatNumber(count)}
                        </span>
                        <span className="text-xs text-gray-400 tabular-nums">{pct.toFixed(0)}%</span>
                      </div>
                    </div>
                    <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${s?.bg ?? "bg-gray-400"}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent reports */}
      <Card className="border-gray-200 shadow-none">
        <CardHeader className="pb-3 flex-row items-center justify-between">
          <CardTitle className="text-sm font-medium">So&apos;nggi murojaatlar</CardTitle>
          <Link
            href="/dashboard/reports"
            className="text-xs text-blue-600 hover:text-blue-700 font-medium"
          >
            Hammasi →
          </Link>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-y border-gray-100 dark:border-gray-800 text-left text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                  <th className="px-4 sm:px-6 py-2.5 font-medium">ID</th>
                  <th className="px-4 sm:px-6 py-2.5 font-medium">Tur</th>
                  <th className="px-4 sm:px-6 py-2.5 font-medium">Holat</th>
                  <th className="px-4 sm:px-6 py-2.5 font-medium hidden sm:table-cell">Foydalanuvchi</th>
                  <th className="px-4 sm:px-6 py-2.5 font-medium hidden md:table-cell">Sana</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50 dark:divide-gray-800">
                {(data?.recentReports ?? []).map((r) => (
                  <tr key={r.id} className="hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-colors">
                    <td className="px-4 sm:px-6 py-3 font-mono text-blue-700 dark:text-blue-400 text-xs">{r.tracking_id}</td>
                    <td className="px-4 sm:px-6 py-3 text-gray-700 dark:text-gray-300">
                      {INCIDENT_LABELS[r.incident_type] ?? r.incident_type}
                    </td>
                    <td className="px-4 sm:px-6 py-3">
                      <Badge className={STATUS_COLORS[r.status]}>
                        {STATUS_LABELS[r.status] ?? r.status}
                      </Badge>
                    </td>
                    <td className="px-4 sm:px-6 py-3 text-gray-500 dark:text-gray-400 hidden sm:table-cell">
                      {r.user?.full_name ?? r.user?.username ?? "—"}
                    </td>
                    <td className="px-4 sm:px-6 py-3 text-gray-400 dark:text-gray-500 text-xs whitespace-nowrap hidden md:table-cell">
                      {formatDate(r.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {(data?.recentReports ?? []).length === 0 && (
              <p className="text-center text-gray-400 py-12 text-sm">Murojaatlar yo&apos;q</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function EmptyChart({ text }: { text: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-[200px] text-gray-400">
      <Inbox className="w-8 h-8 mb-2" strokeWidth={1.5} />
      <p className="text-sm">{text}</p>
    </div>
  );
}
