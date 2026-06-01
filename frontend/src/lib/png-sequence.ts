






export class PngSequence {
  private images = new Map<number, HTMLImageElement>();
  private loading = new Set<number>();
  private failed = new Set<number>();
  public readonly basePath: string;
  public readonly pad: number;
  public readonly total: number;
  public readonly ext: string;

  constructor(total: number, basePath = "/hero/", pad = 4, ext = "webp") {
    this.total = total;
    this.basePath = basePath;
    this.pad = pad;
    this.ext = ext;
  }

  pathFor(i: number) {
    return `${this.basePath}${String(i).padStart(this.pad, "0")}.${this.ext}`;
  }

  load(i: number): Promise<HTMLImageElement | null> {
    if (this.failed.has(i)) return Promise.resolve(null);
    const cached = this.images.get(i);
    if (cached) return Promise.resolve(cached);
    if (this.loading.has(i)) {
      return new Promise((resolve) => {
        let waited = 0;
        const t = setInterval(() => {
          if (this.images.has(i)) { clearInterval(t); resolve(this.images.get(i)!); }
          waited += 30;
          if (waited >= 600) { clearInterval(t); resolve(null); }
        }, 30);
      });
    }
    this.loading.add(i);
    return new Promise((resolve) => {
      const img = new window.Image();
      const timeout = window.setTimeout(() => {
        this.loading.delete(i);
        this.failed.add(i);
        resolve(null);
      }, 900);
      img.crossOrigin = "anonymous";
      img.onload = () => {
        window.clearTimeout(timeout);
        this.images.set(i, img);
        this.loading.delete(i);
        resolve(img);
      };
      img.onerror = () => {
        window.clearTimeout(timeout);
        this.loading.delete(i);
        this.failed.add(i);
        resolve(null);
      };
      img.src = this.pathFor(i);
    });
  }

  preload(from: number, to: number, concurrent = 6): Promise<void> {
    return new Promise((resolveAll) => {
      const queue: number[] = [];
      for (let i = from; i <= to; i++) queue.push(i);
      let inflight = 0;
      const tick = () => {
        if (queue.length === 0 && inflight === 0) { resolveAll(); return; }
        while (inflight < concurrent && queue.length) {
          const i = queue.shift()!;
          inflight++;
          this.load(i).then(() => { inflight--; tick(); });
        }
      };
      tick();
    });
  }

  get(i: number): HTMLImageElement | null {
    return this.images.get(i) ?? null;
  }

  preloadWindow(center: number, before: number, after: number): void {
    const lo = Math.max(0, center - before);
    const hi = Math.min(this.total - 1, center + after);
    for (let i = lo; i <= hi; i++) {
      if (this.images.has(i) || this.loading.has(i) || this.failed.has(i)) continue;
      this.load(i);
    }
  }

  nearest(i: number, radius = 8): HTMLImageElement | null {
    const exact = this.get(i);
    if (exact) return exact;
    for (let d = 1; d <= radius; d++) {
      const prev = this.get(i - d);
      if (prev) return prev;
      const next = this.get(i + d);
      if (next) return next;
    }
    return null;
  }

  



  static async probeTotal(basePath = "/hero/", pad = 4, max = 600, ext = "webp"): Promise<number> {
    const exists = async (i: number) => {
      try {
        const r = await fetch(`${basePath}${String(i).padStart(pad, "0")}.${ext}`, { method: "HEAD", cache: "no-store" });
        return r.ok;
      } catch { return false; }
    };
    
    let lo = 0, hi = 1;
    while (hi < max && await exists(hi)) { lo = hi; hi *= 2; }
    hi = Math.min(hi, max);
    while (lo + 1 < hi) {
      const mid = (lo + hi) >> 1;
      if (await exists(mid)) lo = mid; else hi = mid;
    }
    return lo + 1;
  }
}

export function drawContain(
  canvas: HTMLCanvasElement,
  img: HTMLImageElement,
  scale = 1,
  yOffset = 0,
  xOffset = 0,
  mode: "contain" | "cover" = "contain"
) {
  
  const dpr = Math.min(window.devicePixelRatio || 1, 1.25);
  const cw = canvas.clientWidth, ch = canvas.clientHeight;
  const tw = Math.round(cw * dpr), th = Math.round(ch * dpr);
  if (canvas.width !== tw) canvas.width = tw;
  if (canvas.height !== th) canvas.height = th;
  const ctx = canvas.getContext("2d", { alpha: true, desynchronized: true } as CanvasRenderingContext2DSettings);
  if (!ctx) return;
  ctx.clearRect(0, 0, tw, th);
  const fit = mode === "cover"
    ? Math.max(tw / img.width, th / img.height)
    : Math.min(tw / img.width, th / img.height);
  const r = fit * scale;
  const w = img.width * r;
  const h = img.height * r;
  
  const y = (th - h) / 2 + th * yOffset;
  const x = (tw - w) / 2 + tw * xOffset;
  ctx.drawImage(img, x, y, w, h);
}
