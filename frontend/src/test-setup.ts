import "@testing-library/jest-dom/vitest";

const canvasContext = {
  fillStyle: "",
  font: "",
  fillRect: () => undefined,
  fillText: () => undefined,
  measureText: () => ({ width: 1 })
} as unknown as CanvasRenderingContext2D;

Object.defineProperty(HTMLCanvasElement.prototype, "getContext", { value: () => canvasContext });
Object.defineProperty(HTMLCanvasElement.prototype, "toDataURL", { value: () => "data:image/png;base64,test" });
