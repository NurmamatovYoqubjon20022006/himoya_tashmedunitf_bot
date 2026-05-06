import { prisma } from "@/lib/prisma";
import { NextRequest } from "next/server";
import { getToken } from "next-auth/jwt";
import { jsonResponse } from "@/lib/utils";

export async function PATCH(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const token = await getToken({ req, secret: process.env.AUTH_SECRET });
  if (!token) return jsonResponse({ error: "Unauthorized" }, 401);

  try {
    const { id } = await params;
    const userId = parseInt(id);
    const body = (await req.json()) as { is_blocked?: boolean };

    const data: Record<string, unknown> = {};
    if (typeof body.is_blocked === "boolean") data.is_blocked = body.is_blocked;

    if (Object.keys(data).length === 0) {
      return jsonResponse({ error: "O'zgartirish uchun maydon yo'q" }, 400);
    }

    const user = await prisma.user.update({
      where: { id: userId },
      data,
      select: {
        id: true, telegram_id: true, full_name: true,
        username: true, is_blocked: true,
      },
    });
    // BigInt → string (telegram_id)
    return jsonResponse({
      ...user,
      telegram_id: user.telegram_id.toString(),
    });
  } catch (err) {
    console.error("[/api/users/id] PATCH error:", err);
    return jsonResponse({ error: "Server xatosi", detail: String(err) }, 500);
  }
}
