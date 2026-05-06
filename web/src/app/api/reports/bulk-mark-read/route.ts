import { prisma } from "@/lib/prisma";
import { NextRequest } from "next/server";
import { getToken } from "next-auth/jwt";
import { jsonResponse } from "@/lib/utils";

/**
 * POST /api/reports/bulk-mark-read
 *
 * Barcha NEW murojaatlarni IN_REVIEW holatiga o'tkazadi (komissiya ko'rdi).
 * Admin izohga "Bulk: ko'rildi by <admin>" qo'shiladi.
 */
export async function POST(req: NextRequest) {
  const token = await getToken({ req, secret: process.env.AUTH_SECRET });
  if (!token) return jsonResponse({ error: "Unauthorized" }, 401);

  try {
    const adminName = (token.name as string) || (token.email as string) || "admin";
    const stamp = new Date().toISOString().slice(0, 16).replace("T", " ");
    const noteSuffix = `\n— ${adminName} (${stamp}): toplu ko'rildi`;

    // Transaction: NEW murojaatlar id'larini olamiz, status va izohni yangilaymiz
    const result = await prisma.$transaction(async (tx) => {
      const news = await tx.report.findMany({
        where: { status: "NEW" },
        select: { id: true },
      });
      if (news.length === 0) return { count: 0 };

      const ids = news.map((r) => r.id);
      await tx.$executeRaw`
        UPDATE reports
        SET status = 'IN_REVIEW',
            updated_at = NOW(),
            admin_note = COALESCE(admin_note, '') || ${noteSuffix}
        WHERE id = ANY(${ids}::int[])
      `;
      return { count: ids.length };
    });

    return jsonResponse({ ok: true, updated: result.count });
  } catch (err) {
    console.error("[/api/reports/bulk-mark-read] POST error:", err);
    return jsonResponse({ error: "Server xatosi", detail: String(err) }, 500);
  }
}
