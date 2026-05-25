import dotenv from "dotenv";

dotenv.config();

export const config = {
  port: Number(process.env.PORT || 3000),
  aiServiceUrl: process.env.AI_SERVICE_URL || "http://127.0.0.1:8001",
  databaseUrl: process.env.DATABASE_URL || "",
};
