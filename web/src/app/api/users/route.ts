import { prisma } from "@/lib/prisma";
import { NextRequest } from "next/server";
import { getToken } from "next-auth/jwt";
import { type Prisma } from "@prisma/client";
import { jsonResponse } from "@/lib/utils";

export async function GET(req: NextRequest) {
  const token = await getToken({ req, secret: process.env.AUTH_SECRET });
  if (!token) return jsonResponse({ error: "Unauthorized" }, 401);

  try {
    const { searchParams } = new URL(req.url);
    const page = Math.max(1, parseInt(searchParams.get("page") ?? "1"));
    const limit = Math.min(100, parseInt(searchParams.get("limit") ?? "20"));
    const search = searchParams.get("search") ?? undefined;

    const where: Prisma.UserWhereInput = search
      ? {
          OR: [
            { full_name: { contains: search, mode: "insensitive" } },
            { username: { contains: search, mode: "insensitive" } },
            { phone: { contains: search, mode: "insensitive" } },
            { direction: { contains: search, mode: "insensitive" } },
          ],
        }
      : {};

    const [users, total] = await Promise.all([
      prisma.user.findMany({
        where,
        skip: (page - 1) * limit,
        take: limit,
        orderBy: { created_at: "desc" },
        include: { _count: { select: { reports: true } } },
      }),
      prisma.user.count({ where }),
    ]);

    return jsonResponse({ users, total, page, limit });
  } catch (err) {
    console.error("[/api/users] GET error:", err);
    return jsonResponse({ error: "Server xatosi", detail: String(err) }, 500);
  }
}
