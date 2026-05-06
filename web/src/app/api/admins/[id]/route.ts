import { prisma } from "@/lib/prisma";
import { NextRequest } from "next/server";
import { getToken } from "next-auth/jwt";
import { jsonResponse } from "@/lib/utils";
import bcrypt from "bcryptjs";

const VALID_ROLES = new Set(["admin", "commission", "psychologist", "legal", "user"]);

// Loyiha asoschilari — hech kim tegisha olmaydi (faqat o'zi).
// Username pastki harflarda solishtiriladi.
const FOUNDER_USERNAMES = new Set(["admin", "yoqubjon"]);
const isFounderUsername = (u: string) => FOUNDER_USERNAMES.has(u.toLowerCase());

export async function PATCH(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const token = await getToken({ req, secret: process.env.AUTH_SECRET });
  if (!token) return jsonResponse({ error: "Unauthorized" }, 401);
  if (token.role !== "admin") {
    return jsonResponse({ error: "Faqat super admin o'zgartira oladi" }, 403);
  }

  try {
    const { id } = await params;
    const adminId = parseInt(id);

    const target = await prisma.adminUser.findUnique({
      where: { id: adminId },
      select: { id: true, username: true, role: true },
    });
    if (!target) return jsonResponse({ error: "Admin topilmadi" }, 404);

    const requesterIsTarget = String(token.id) === String(adminId);
    const isFounder = isFounderUsername(target.username);

    // Founder'ni faqat o'zi o'zgartira oladi
    if (isFounder && !requesterIsTarget) {
      return jsonResponse(
        { error: "Loyiha asoschisini boshqa hech kim o'zgartira olmaydi" },
        403,
      );
    }

    const body = (await req.json()) as {
      is_active?: boolean;
      role?: string;
      full_name?: string;
      password?: string;
    };

    const data: Record<string, unknown> = {};
    if (typeof body.is_active === "boolean") data.is_active = body.is_active;
    if (body.role && VALID_ROLES.has(body.role)) data.role = body.role;
    if (body.full_name?.trim()) data.full_name = body.full_name.trim();
    if (body.password) {
      if (body.password.length < 8) {
        return jsonResponse({ error: "Parol kamida 8 ta belgi" }, 400);
      }
      data.password_hash = await bcrypt.hash(body.password, 12);
    }

    // Founder o'zining role va is_active'ini o'zgartira olmaydi
    // (deactivate qilib o'z hisobini yo'qotmasligi uchun)
    if (isFounder) {
      delete data.role;
      delete data.is_active;
    }

    if (Object.keys(data).length === 0) {
      return jsonResponse({ error: "O'zgartirish uchun maydon yo'q" }, 400);
    }

    const updated = await prisma.adminUser.update({
      where: { id: adminId },
      data,
      select: {
        id: true, username: true, full_name: true, role: true,
        is_active: true, last_login: true, created_at: true,
      },
    });
    return jsonResponse(updated);
  } catch (err) {
    console.error("[/api/admins/id] PATCH error:", err);
    return jsonResponse({ error: "Server xatosi", detail: String(err) }, 500);
  }
}

export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const token = await getToken({ req, secret: process.env.AUTH_SECRET });
  if (!token) return jsonResponse({ error: "Unauthorized" }, 401);
  if (token.role !== "admin") {
    return jsonResponse({ error: "Faqat super admin o'chira oladi" }, 403);
  }

  try {
    const { id } = await params;
    const adminId = parseInt(id);

    const target = await prisma.adminUser.findUnique({
      where: { id: adminId },
      select: { id: true, username: true },
    });
    if (!target) return jsonResponse({ error: "Admin topilmadi" }, 404);

    if (isFounderUsername(target.username)) {
      return jsonResponse(
        { error: "Loyiha asoschisini o'chirib bo'lmaydi" },
        403,
      );
    }

    if (String(token.id) === String(adminId)) {
      return jsonResponse({ error: "O'zingizni o'chira olmaysiz" }, 400);
    }

    await prisma.adminUser.delete({ where: { id: adminId } });
    return jsonResponse({ ok: true });
  } catch (err) {
    console.error("[/api/admins/id] DELETE error:", err);
    return jsonResponse({ error: "Server xatosi", detail: String(err) }, 500);
  }
}
