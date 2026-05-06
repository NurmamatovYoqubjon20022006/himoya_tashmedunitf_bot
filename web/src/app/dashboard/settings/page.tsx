"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ROLE_LABELS } from "@/lib/utils";
import { Shield, User, Bell, FileText, BellRing, BellOff } from "lucide-react";

export default function SettingsPage() {
  const { data: session } = useSession();
  const role = (session?.user as { role?: string })?.role ?? "";
  const [notifPerm, setNotifPerm] = useState<NotificationPermission | "unsupported">("default");

  useEffect(() => {
    if (typeof window === "undefined" || !("Notification" in window)) {
      setNotifPerm("unsupported");
    } else {
      setNotifPerm(Notification.permission);
    }
  }, []);

  async function requestNotif() {
    if (!("Notification" in window)) return;
    const result = await Notification.requestPermission();
    setNotifPerm(result);
    if (result === "granted") {
      new Notification("✅ Bildirishnomalar yoqildi", {
        body: "Yangi murojaatlar haqida xabar olasiz",
        icon: "/logo.jpg",
      });
    }
  }

  return (
    <div className="space-y-5 sm:space-y-6 max-w-3xl">
      <div>
        <h1 className="text-xl sm:text-2xl font-semibold text-gray-900 dark:text-white dark:text-white tracking-tight">Sozlamalar</h1>
        <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Tizim va profil ma&apos;lumotlari</p>
      </div>

      {/* Profile */}
      <Card className="border-gray-200 shadow-none">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <User className="w-4 h-4 text-blue-600" />
            <CardTitle className="text-sm font-medium">Profil</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-3 sm:gap-4 flex-wrap">
            <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white font-semibold text-base sm:text-lg flex-shrink-0">
              {session?.user?.name?.[0]?.toUpperCase() ?? "A"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-gray-900 dark:text-white dark:text-white truncate">{session?.user?.name}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 truncate">@{session?.user?.email}</p>
            </div>
            <Badge className="bg-blue-100 text-blue-700">
              {ROLE_LABELS[role] ?? role}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Bot info */}
      <Card className="border-gray-200 shadow-none">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-blue-600" />
            <CardTitle className="text-sm font-medium">Bot haqida</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-start gap-4 mb-4 pb-4 border-b border-gray-100">
            <div className="relative w-16 h-16 rounded-full overflow-hidden flex-shrink-0 ring-2 ring-blue-100">
              <Image
                src="/logo.jpg"
                alt="TDTU Termiz filiali logo"
                fill
                sizes="64px"
                className="object-cover"
              />
            </div>
            <div className="min-w-0 flex-1">
              <p className="font-semibold text-gray-900 dark:text-white">Himoya Bot</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                Toshkent Davlat Tibbiyot Universiteti — Termiz filiali
              </p>
            </div>
          </div>
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <dt className="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wide mb-1">Bot</dt>
              <dd className="text-gray-900 dark:text-white font-medium">@himoya_tashmedunitf_bot</dd>
            </div>
            <div>
              <dt className="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wide mb-1">Muassasa</dt>
              <dd className="text-gray-900 dark:text-white font-medium">TDTU Termiz filiali</dd>
            </div>
            <div>
              <dt className="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wide mb-1">Asos</dt>
              <dd className="text-gray-900 dark:text-white font-medium">150-son buyruq (2026)</dd>
            </div>
            <div>
              <dt className="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wide mb-1">Versiya</dt>
              <dd className="text-gray-900 dark:text-white font-medium">1.0.0</dd>
            </div>
          </dl>

          {/* Yaratuvchi */}
          <div className="mt-5 pt-5 border-t border-gray-100 dark:border-gray-800">
            <p className="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wide mb-2">
              Loyiha yaratuvchisi
            </p>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center text-white font-bold flex-shrink-0">
                Y
              </div>
              <div className="min-w-0">
                <p className="text-gray-900 dark:text-white font-semibold">Yoqubjon</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Super admin · Loyiha asoschisi
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Documents */}
      <Card className="border-gray-200 shadow-none">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-blue-600" />
            <CardTitle className="text-sm font-medium">Hujjatlar</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            Bot O&apos;zbekiston Respublikasi Oliy ta&apos;lim, fan va innovatsiyalar
            vazirligining 2026-yil 20-apreldagi <b>150-sonli buyrug&apos;i</b> asosida
            ishlab chiqilgan — &laquo;Ta&apos;lim muassasalarida o&apos;quvchi-talaba qizlarning
            huquq va xavfsizligini ta&apos;minlash hamda shilqimlik (harassment), tazyiq
            holatlarining oldini olish to&apos;g&apos;risida&raquo;.
          </p>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card className="border-gray-200 shadow-none">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <Bell className="w-4 h-4 text-blue-600" />
            <CardTitle className="text-sm font-medium">Bildirishnomalar</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Browser notification */}
          <div className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-800">
            {notifPerm === "granted" ? (
              <BellRing className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
            ) : notifPerm === "denied" ? (
              <BellOff className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            ) : (
              <Bell className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                Brauzer bildirishnomalari
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                {notifPerm === "granted"
                  ? "Yoqilgan — yangi murojaatlar haqida xabar olasiz"
                  : notifPerm === "denied"
                  ? "Bloklangan — brauzer sozlamalaridan ruxsat bering"
                  : notifPerm === "unsupported"
                  ? "Brauzeringiz bildirishnomalarni qo'llab-quvvatlamaydi"
                  : "Yangi murojaatlar haqida xabar olish uchun yoqing"}
              </p>
            </div>
            {notifPerm === "default" && (
              <Button size="sm" onClick={requestNotif}>
                Yoqish
              </Button>
            )}
            {notifPerm === "granted" && (
              <Badge className="bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300">
                Faol
              </Badge>
            )}
          </div>

          {/* Telegram info */}
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            Yangi murojaat kelganda Telegram orqali admin ham bildirishnoma oladi.
            Bot token va admin ID&apos;lar{" "}
            <code className="bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded text-xs font-mono">.env</code>{" "}
            faylida sozlanadi.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
