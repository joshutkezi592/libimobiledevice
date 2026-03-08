import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  const dir = path.join(process.cwd(), "public", "downloads");

  if (!fs.existsSync(dir)) {
    return NextResponse.json([]);
  }

  const files = fs.readdirSync(dir).filter((f) => f.endsWith(".mp3"));

  const tracks = files.map((file) => {
    const stat = fs.statSync(path.join(dir, file));
    const name = file.replace(/\.mp3$/i, "").replace(/[-_]/g, " ");
    return {
      name,
      filename: file,
      url: `/downloads/${file}`,
      size: stat.size,
      addedAt: stat.mtimeMs,
    };
  });

  // Sort newest first
  tracks.sort((a, b) => b.addedAt - a.addedAt);

  return NextResponse.json(tracks);
}
