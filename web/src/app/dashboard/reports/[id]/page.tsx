"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label, Select, Textarea } from "@/components/ui/input";
import {
  FACULTY_LABELS,
  INCIDENT_LABELS,
  STATUS_COLORS,
  STATUS_LABELS,
  USER_TYPE_LABELS,
  formatDate,
} from "@/lib/utils";
import {
  ArrowLeft,
  Save,
  Loader2,
  MapPin,
  Calendar,
  Paperclip,
  Phone,
  User as UserIcon,
} from "lucide-react";
import { toast } from "sonner";

interface Report {
  id: number;
  tracking_id: string;
  incident_type: string;
  status: string;
  description: string;
  location?: string;
  incident_date?: string;
  admin_note?: string;
  is_anonymous: boolean;
  created_at: string;
  updated_at: string;
  user?: {
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
    language: string;
  } | null;
  attachments: { id: number; file_id: string; file_type: string; created_at: string }[];
}

export default function ReportDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState("");
  const [adminNote, setAdminNote] = useState("");

  useEffect(() => {
    fetch(`/api/reports/${id}`)
      .then((r) => r.json())
      .then((data: Report) => {
        setReport(data);
        setStatus(data.status);
        setAdminNote(data.admin_note ?? "");
        setLoading(false);
      });
  }, [id]);

  async function handleSave() {
    setSaving(true);
    const res = await fetch(`/api/reports/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, admin_note: adminNote }),
    });

    setSaving(false);
    if (res.ok) {
      const updated = await res.json() as Report;
      setReport((prev) => prev ? { ...prev, ...updated } : null);
      toast.success("Saqlandi");
    } else {
      toast.error("Xato yuz berdi");
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-16">
        <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!report) return <p className="text-gray-500">Murojaat topilmadi</p>;

  return (
    <div className="space-y-5 sm:space-y-6 max-w-5xl">
      {/* Header */}
      <div className="flex items-center gap-2 sm:gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.back()} className="flex-shrink-0">
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <div className="min-w-0 flex-1">
          <h1 className="text-base sm:text-xl font-semibold text-gray-900 dark:text-white font-mono tracking-tight truncate">
            {report.tracking_id}
          </h1>
          <p className="text-gray-500 dark:text-gray-400 text-xs mt-0.5">{formatDate(report.created_at)}</p>
        </div>
        <Badge className={STATUS_COLORS[report.status]}>
          {STATUS_LABELS[report.status]}
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Main info */}
        <div className="lg:col-span-2 space-y-4">
          <Card className="border-gray-200 shadow-none">
            <CardHeader>
              <CardTitle className="text-sm font-medium">Murojaat tafsilotlari</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
                  Hodisa turi
                </p>
                <p className="text-gray-900 dark:text-white">
                  {INCIDENT_LABELS[report.incident_type] ?? report.incident_type}
                </p>
              </div>

              <div>
                <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
                  Tavsif
                </p>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                  {report.description}
                </p>
              </div>

              {report.location && (
                <div className="flex items-start gap-2">
                  <MapPin className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5" />
                  <p className="text-gray-700 dark:text-gray-300">{report.location}</p>
                </div>
              )}

              {report.incident_date && (
                <div className="flex items-start gap-2">
                  <Calendar className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5" />
                  <p className="text-gray-700 dark:text-gray-300">{report.incident_date}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Attachments */}
          {report.attachments.length > 0 && (
            <Card className="border-gray-200 shadow-none">
              <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Paperclip className="w-4 h-4" />
                  Ilova fayllar ({report.attachments.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {report.attachments.map((att) => (
                    <div
                      key={att.id}
                      className="flex items-center gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
                    >
                      <span className="text-2xl">
                        {att.file_type === "photo"
                          ? "🖼️"
                          : att.file_type === "video"
                          ? "🎥"
                          : att.file_type === "audio"
                          ? "🎵"
                          : "📎"}
                      </span>
                      <div>
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-200 capitalize">
                          {att.file_type}
                        </p>
                        <p className="text-xs text-gray-400 dark:text-gray-500 font-mono truncate max-w-xs">
                          {att.file_id.slice(0, 30)}...
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Admin actions */}
          <Card className="border-gray-200 shadow-none">
            <CardHeader>
              <CardTitle className="text-sm font-medium">Admin qaydlari</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Holat</Label>
                <Select value={status} onChange={setStatus}>
                  {(["NEW","IN_REVIEW","RESOLVED","REJECTED"] as const).map((k) => (
                    <option key={k} value={k}>{STATUS_LABELS[k]}</option>
                  ))}
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Izoh</Label>
                <Textarea
                  value={adminNote}
                  onChange={(e) => setAdminNote(e.target.value)}
                  placeholder="Admin izohi..."
                  rows={4}
                />
              </div>

              <Button onClick={handleSave} disabled={saving}>
                {saving && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                <Save className="w-4 h-4 mr-2" />
                Saqlash
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <Card className="border-gray-200 shadow-none">
            <CardHeader>
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <UserIcon className="w-4 h-4" />
                Murojaatchi
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              {report.user ? (
                <>
                  <div>
                    <p className="text-gray-500 dark:text-gray-400 text-xs">F.I.O</p>
                    <p className="font-medium text-gray-900 dark:text-white">{report.user.full_name ?? "—"}</p>
                  </div>
                  {report.user.phone && (
                    <div>
                      <p className="text-gray-500 dark:text-gray-400 text-xs">Telefon</p>
                      <a
                        href={`tel:${report.user.phone}`}
                        className="font-medium font-mono text-blue-600 dark:text-blue-400 flex items-center gap-1 hover:underline"
                      >
                        <Phone className="w-3 h-3" />
                        {report.user.phone}
                      </a>
                    </div>
                  )}
                  {report.user.user_type && (
                    <div>
                      <p className="text-gray-500 dark:text-gray-400 text-xs">Maqom</p>
                      <p className="font-medium text-gray-900 dark:text-gray-200">
                        {USER_TYPE_LABELS[report.user.user_type] ?? report.user.user_type}
                      </p>
                    </div>
                  )}
                  {report.user.faculty && (
                    <div>
                      <p className="text-gray-500 dark:text-gray-400 text-xs">Fakultet</p>
                      <p className="font-medium text-gray-900 dark:text-gray-200">
                        {FACULTY_LABELS[report.user.faculty] ?? report.user.faculty}
                      </p>
                    </div>
                  )}
                  {report.user.course && (
                    <div>
                      <p className="text-gray-500 dark:text-gray-400 text-xs">Kurs</p>
                      <p className="font-medium text-gray-900 dark:text-gray-200">{report.user.course}-kurs</p>
                    </div>
                  )}
                  {report.user.direction && (
                    <div>
                      <p className="text-gray-500 dark:text-gray-400 text-xs">Yo'nalish</p>
                      <p className="font-medium text-gray-900 dark:text-gray-200">{report.user.direction}</p>
                    </div>
                  )}
                  {report.user.group_name && (
                    <div>
                      <p className="text-gray-500 dark:text-gray-400 text-xs">Guruh</p>
                      <p className="font-medium text-gray-900 dark:text-gray-200">{report.user.group_name}</p>
                    </div>
                  )}
                  {report.user.position && (
                    <div>
                      <p className="text-gray-500 dark:text-gray-400 text-xs">Lavozim</p>
                      <p className="font-medium text-gray-900 dark:text-gray-200">{report.user.position}</p>
                    </div>
                  )}
                  {report.user.username && (
                    <div>
                      <p className="text-gray-500 dark:text-gray-400 text-xs">Telegram</p>
                      <p className="font-medium text-blue-600 dark:text-blue-400">
                        @{report.user.username}
                      </p>
                    </div>
                  )}
                </>
              ) : (
                <p className="text-gray-400 dark:text-gray-500 italic">Foydalanuvchi ma'lumotlari mavjud emas</p>
              )}
            </CardContent>
          </Card>

          <Card className="border-gray-200 shadow-none">
            <CardHeader>
              <CardTitle className="text-sm font-medium">Vaqt</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div>
                <p className="text-gray-500 dark:text-gray-400 text-xs">Yaratilgan</p>
                <p className="font-medium text-gray-900 dark:text-gray-200">{formatDate(report.created_at)}</p>
              </div>
              <div>
                <p className="text-gray-500 dark:text-gray-400 text-xs">Yangilangan</p>
                <p className="font-medium text-gray-900 dark:text-gray-200">{formatDate(report.updated_at)}</p>
              </div>
            </CardContent>
          </Card>

          {/* Yoqubjon — Super admin */}
          <Card className="border-purple-200 dark:border-purple-900/50 shadow-none bg-gradient-to-br from-purple-50/50 to-blue-50/50 dark:from-purple-950/20 dark:to-blue-950/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0 shadow-sm">
                  Y
                </div>
                <div className="min-w-0 flex-1">
                  <p className="font-semibold text-gray-900 dark:text-white text-sm">Yoqubjon</p>
                  <p className="text-xs text-purple-700 dark:text-purple-300 font-medium">
                    Super admin · Loyiha asoschisi
                  </p>
                </div>
              </div>
              <p className="mt-3 text-xs text-gray-500 dark:text-gray-400 leading-relaxed border-t border-purple-100 dark:border-purple-900/30 pt-3">
                Murojaatni ko&apos;rib chiqishda yordam kerak bo&apos;lsa,
                Super admin bilan bog&apos;laning.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
