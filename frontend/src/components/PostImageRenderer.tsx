import { useEffect, useRef } from "react";

export type PosterPage = { heading: string; body: string };

const WIDTH = 1080;
const HEIGHT = 1440;

function drawWrappedText(context: CanvasRenderingContext2D, text: string, x: number, y: number, maxWidth: number, lineHeight: number): number {
  let line = "";
  let cursor = y;
  for (const character of text) {
    const next = line + character;
    if (context.measureText(next).width > maxWidth && line) {
      context.fillText(line, x, cursor);
      line = character;
      cursor += lineHeight;
    } else {
      line = next;
    }
  }
  if (line) context.fillText(line, x, cursor);
  return cursor + lineHeight;
}

export function paintPoster(canvas: HTMLCanvasElement, page: PosterPage, index: number, title: string): void {
  canvas.width = WIDTH;
  canvas.height = HEIGHT;
  const context = canvas.getContext("2d");
  if (!context) return;
  context.fillStyle = "#f7f6f0";
  context.fillRect(0, 0, WIDTH, HEIGHT);
  context.fillStyle = "#da4b37";
  context.fillRect(0, 0, WIDTH, 28);
  context.fillStyle = "#1d2420";
  context.font = "500 34px sans-serif";
  context.fillText(`小红书图文 · ${String(index + 1).padStart(2, "0")}/05`, 84, 110);
  context.fillStyle = "#da4b37";
  context.font = "700 40px sans-serif";
  drawWrappedText(context, title, 84, 210, 900, 58);
  context.fillStyle = "#1d2420";
  context.font = "700 72px sans-serif";
  const bodyStart = drawWrappedText(context, page.heading, 84, 430, 900, 94);
  context.fillStyle = "#536158";
  context.font = "400 42px sans-serif";
  drawWrappedText(context, page.body, 84, bodyStart + 80, 900, 68);
  context.fillStyle = "#ccd4cd";
  context.fillRect(84, 1300, 912, 2);
  context.fillStyle = "#536158";
  context.font = "400 28px sans-serif";
  context.fillText("内容仅供发布前人工审核与修改", 84, 1360);
}

function saveCanvas(canvas: HTMLCanvasElement, filename: string): void {
  const link = document.createElement("a");
  link.download = filename;
  link.href = canvas.toDataURL("image/png");
  link.click();
}

export function downloadPoster(page: PosterPage, index: number, title: string): void {
  const canvas = document.createElement("canvas");
  paintPoster(canvas, page, index, title);
  saveCanvas(canvas, `小红书图文-${String(index + 1).padStart(2, "0")}.png`);
}

export function PostImageRenderer({ page, index, title }: { page: PosterPage; index: number; title: string }) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    if (ref.current) paintPoster(ref.current, page, index, title);
  }, [page, index, title]);
  return <canvas ref={ref} className="poster-preview" width={WIDTH} height={HEIGHT} aria-label={`第 ${index + 1} 张海报预览`} />;
}
