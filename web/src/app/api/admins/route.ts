import { prisma } from "@/lib/prisma";
import { NextRequest } from "next/server";
import { getToken } from "next-auth/jwt";
import { jsonResponse } from "@/lib/utils";
import bcrypt from "bcryptjs";

export async function GET(req: NextRequest) {
  const token = await getToken({ req, secret: process.env.AUTH_SECRET });
  if (!token) return jsonResponse({ error: "Unauthorized" }, 401);

  try {
    const admins = await prisma.adminUser.findMany({
      orderBy: { created_at: "desc" },
      select: {
        id: true,
        username: true,
        full_name: true,
        role: true,
        is_active: true,
        last_login: true,
        created_at: true,
      },
    });
    return jsonResponse({ admins });
  } catch (err) {
    console.error("[/api/admins] GET error:", err);
    return jsonResponse({ error: "Server xatosi", detail: String(err) }, 500);
  }
}

export async function POST(req: NextRequest) {
  const token = await getToken({ req, secret: process.env.AUTH_SECRET });
  if (!token) return jsonResponse({ error: "Unauthorized" }, 401);

  try {
    const body = await req.json() as {
      username?: string;
      full_name?: string;
      password?: string;
      role?: string;
    };

    if (!body.username?.trim() || !body.full_name?.trim() || !body.password) {
      return jsonResponse({ error: "Majburiy maydonlar to'ldirilmagan" }, 400);
    }
    if (body.password.length < 8) {
      return jsonResponse({ error: "Parol kamida 8 ta belgi bo'lishi kerak" }, 400);
    }

    const exists = await prisma.adminUser.findUnique({ where: { username: body.username } });
    if (exists) return jsonResponse({ error: "Bu username allaqachon mavjud" }, 409);

    const hash = await bcrypt.hash(body.password, 12);
    const admin = await prisma.adminUser.create({
      data: {
        username: body.username,
        full_name: body.full_name,
        password_hash: hash,
        role: body.role ?? "commission",
      },
      select: { id: true, username: true, full_name: true, role: true, created_at: true },
    });

    return jsonResponse(admin, 201);
  } catch (err) {
    console.error("[/api/admins] POST error:", err);
    return jsonResponse({ error: "Server xatosi", detail: String(err) }, 500);
  }
}
