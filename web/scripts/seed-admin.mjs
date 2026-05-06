/**
 * Birinchi superadmin yaratish uchun seed script.
 * Ishlatish: node scripts/seed-admin.mjs
 */

import { PrismaClient } from "@prisma/client";
import bcrypt from "bcryptjs";
import readline from "readline";

const prisma = new PrismaClient();

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const ask = (q) => new Promise((resolve) => rl.question(q, resolve));

async function main() {
  console.log("\n=== Himoya Admin — Superadmin yaratish ===\n");

  const username = await ask("Foydalanuvchi nomi (login): ");
  const fullName = await ask("To'liq ism: ");
  const password = await ask("Parol (min 8 belgi): ");

  if (password.length < 8) {
    console.error("Parol kamida 8 ta belgi bo'lishi kerak!");
    process.exit(1);
  }

  const existing = await prisma.adminUser.findUnique({ where: { username } });
  if (existing) {
    console.error(`"${username}" username allaqachon mavjud!`);
    process.exit(1);
  }

  const hash = await bcrypt.hash(password, 12);

  const admin = await prisma.adminUser.create({
    data: {
      username,
      full_name: fullName,
      password_hash: hash,
      role: "admin",
      is_active: true,
    },
  });

  console.log(`\n✅ Superadmin yaratildi: ${admin.full_name} (@${admin.username})`);
  console.log("Admin panelga kirish: http://localhost:3000/login\n");
}

main()
  .catch((e) => { console.error(e); process.exit(1); })
  .finally(async () => { await prisma.$disconnect(); rl.close(); });
