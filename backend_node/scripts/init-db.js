import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import dotenv from "dotenv";
import pg from "pg";

dotenv.config();

const { Client } = pg;
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..", "..");
const databaseDir = path.join(rootDir, "ai_fastapi_postgresql", "database");

const scripts = [
  "001_create_tables.sql",
  "002_create_indexes.sql",
  "005_seed_data.sql",
];

async function main() {
  if (!process.env.DATABASE_URL) {
    throw new Error("DATABASE_URL is required. Copy .env.example to .env and set your PostgreSQL connection string.");
  }

  const client = new Client({ connectionString: process.env.DATABASE_URL });
  await client.connect();
  try {
    for (const script of scripts) {
      const sql = await fs.readFile(path.join(databaseDir, script), "utf8");
      await client.query(sql);
      console.log(`Applied ${script}`);
    }
  } finally {
    await client.end();
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
