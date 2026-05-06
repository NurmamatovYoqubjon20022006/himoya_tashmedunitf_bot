import { prisma } from "@/lib/prisma";
import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { jsonResponse } from "@/lib/utils";

async function checkAuth(req: NextRequest) {
  const token = await getToken({ req, secret: process.env.AUTH_SECRET });
  return token;
}

export async function GET(req: NextRequest) {
  const token = await checkAuth(req);
  if (!token) return jsonResponse({ error: "Unauthorized" }, 401);

  try {
    const [
      totalReports,
      newReports,
      inReviewReports,
      resolvedReports,
      rejectedReports,
      totalUsers,
      recentReports,
      byIncidentType,
      last7Days,
    ] = await Promise.all([
      prisma.report.count(),
      prisma.report.count({ where: { status: "NEW" } }),
      prisma.report.count({ where: { status: "IN_REVIEW" } }),
      prisma.report.count({ where: { status: "RESOLVED" } }),
      prisma.report.count({ where: { status: "REJECTED" } }),
      prisma.user.count(),
      prisma.report.findMany({
        take: 5,
        orderBy: { created_at: "desc" },
        include: { user: { select: { full_name: true, username: true } } },
      }),
      prisma.report.groupBy({
        by: ["incident_type"],
        _count: { incident_type: true },
      }),
      // generate_series — 7 kun ham bo'lmasligi uchun (hatto count=0)
      prisma.$queryRaw<{ day: Date; count: bigint }[]>`
        SELECT d::date AS day,
               COALESCE(COUNT(r.id), 0)::bigint AS count
        FROM generate_series(
          (CURRENT_DATE - INTERVAL '6 days')::date,
          CURRENT_DATE,
          INTERVAL '1 day'
        ) AS d
        LEFT JOIN reports r ON DATE(r.created_at) = d::date
        GROUP BY d
        ORDER BY d
      `,
    ]);

    return jsonResponse({
      stats: {
        total: totalReports,
        new: newReports,
        in_review: inReviewReports,
        resolved: resolvedReports,
        rejected: rejectedReports,
        users: totalUsers,
      },
      recentReports,
      byIncidentType: byIncidentType.map((r) => ({
        type: r.incident_type,
        count: r._count.incident_type,
      })),
      last7Days: last7Days.map((r) => ({
        day: r.day instanceof Date ? r.day.toISOString().split("T")[0] : String(r.day),
        count: Number(r.count),
      })),
    });
  } catch (err) {
    console.error("[/api/stats] error:", err);
    return jsonResponse({ error: "Server xatosi", detail: String(err) }, 500);
  }
}
