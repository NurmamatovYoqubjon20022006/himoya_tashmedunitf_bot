import { prisma } from "@/lib/prisma";
import { NextRequest } from "next/server";
import { getToken } from "next-auth/jwt";
import { ReportStatus } from "@prisma/client";
import { jsonResponse } from "@/lib/utils";

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const token = await getToken({ req, secret: process.env.AUTH_SECRET });
  if (!token) return jsonResponse({ error: "Unauthorized" }, 401);

  try {
    const { id } = await params;
    const report = await prisma.report.findUnique({
      where: { id: parseInt(id) },
      include: { user: true, attachments: true },
    });
    if (!report) return jsonResponse({ error: "Not found" }, 404);
    return jsonResponse(report);
  } catch (err) {
    console.error("[/api/reports/id] GET error:", err);
    return jsonResponse({ error: "Server xatosi", detail: String(err) }, 500);
  }
}

export async function PATCH(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const token = await getToken({ req, secret: process.env.AUTH_SECRET });
  if (!token) return jsonResponse({ error: "Unauthorized" }, 401);

  try {
    const { id } = await params;
    const body = await req.json() as { status?: string; admin_note?: string };

    const data: Record<string, unknown> = {};
    if (body.status) {
      const upper = body.status.toUpperCase();
      if (Object.values(ReportStatus).includes(upper as ReportStatus)) {
        data.status = upper as ReportStatus;
      }
    }
    if (body.admin_note !== undefined) data.admin_note = body.admin_note;

    const report = await prisma.report.update({ where: { id: parseInt(id) }, data });
    return jsonResponse(report);
  } catch (err) {
    console.error("[/api/reports/id] PATCH error:", err);
    return jsonResponse({ error: "Server xatosi", detail: String(err) }, 500);
  }
}

export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const token = await getToken({ req, secret: process.env.AUTH_SECRET });
  if (!token) return jsonResponse({ error: "Unauthorized" }, 401);

  try {
    const { id } = await params;
    await prisma.report.delete({ where: { id: parseInt(id) } });
    return jsonResponse({ ok: true });
  } catch (err) {
    console.error("[/api/reports/id] DELETE error:", err);
    return jsonResponse({ error: "Server xatosi", detail: String(err) }, 500);
  }
}
