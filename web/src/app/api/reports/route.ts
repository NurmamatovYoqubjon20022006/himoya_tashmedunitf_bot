import { prisma } from "@/lib/prisma";
import { NextRequest } from "next/server";
import { getToken } from "next-auth/jwt";
import { type Prisma, ReportStatus, IncidentType } from "@prisma/client";
import { jsonResponse } from "@/lib/utils";

export async function GET(req: NextRequest) {
  const token = await getToken({ req, secret: process.env.AUTH_SECRET });
  if (!token) return jsonResponse({ error: "Unauthorized" }, 401);

  try {
    const { searchParams } = new URL(req.url);
    const page = Math.max(1, parseInt(searchParams.get("page") ?? "1"));
    const limit = Math.min(100, Math.max(1, parseInt(searchParams.get("limit") ?? "20")));
    const statusParam = searchParams.get("status");
    const typeParam = searchParams.get("type");
    const search = searchParams.get("search") ?? undefined;

    const where: Prisma.ReportWhereInput = {};
    if (statusParam && Object.values(ReportStatus).includes(statusParam.toUpperCase() as ReportStatus)) {
      where.status = statusParam.toUpperCase() as ReportStatus;
    }
    if (typeParam && Object.values(IncidentType).includes(typeParam.toUpperCase() as IncidentType)) {
      where.incident_type = typeParam.toUpperCase() as IncidentType;
    }
    if (search) {
      where.OR = [
        { tracking_id: { contains: search, mode: "insensitive" } },
        { description: { contains: search, mode: "insensitive" } },
        { user: { full_name: { contains: search, mode: "insensitive" } } },
        { user: { phone: { contains: search, mode: "insensitive" } } },
        { user: { username: { contains: search, mode: "insensitive" } } },
        { user: { direction: { contains: search, mode: "insensitive" } } },
        { user: { group_name: { contains: search, mode: "insensitive" } } },
        { user: { position: { contains: search, mode: "insensitive" } } },
      ];
    }

    const [reports, total] = await Promise.all([
      prisma.report.findMany({
        where,
        skip: (page - 1) * limit,
        take: limit,
        orderBy: { created_at: "desc" },
        include: {
          user: {
            select: {
              full_name: true,
              username: true,
              telegram_id: true,
              phone: true,
              user_type: true,
              faculty: true,
              course: true,
              direction: true,
              group_name: true,
              position: true,
            },
          },
          attachments: { select: { id: true, file_type: true } },
        },
      }),
      prisma.report.count({ where }),
    ]);

    return jsonResponse({ reports, total, page, limit });
  } catch (err) {
    console.error("[/api/reports] GET error:", err);
    return jsonResponse({ error: "Server xatosi", detail: String(err) }, 500);
  }
}
