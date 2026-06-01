import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function fmt(n: number, digits = 0) {
  return n.toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function compact(n: number, digits = 1) {
  const abs = Math.abs(n);
  if (abs >= 1_000_000) return `${(n / 1_000_000).toFixed(digits).replace(/\.0$/, "")}m`;
  if (abs >= 1_000) return `${(n / 1_000).toFixed(digits).replace(/\.0$/, "")}k`;
  return fmt(n, 0);
}

export function pad(n: number, width = 2) {
  return n.toString().padStart(width, "0");
}

export function clamp(v: number, lo: number, hi: number) {
  return Math.max(lo, Math.min(hi, v));
}
