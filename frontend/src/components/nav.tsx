"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const links = [
  { href: "/", label: "Home" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/simulator", label: "Simulator" },
  { href: "/fia", label: "FIA" },
  { href: "/backtests", label: "Backtests" },
  { href: "/flows", label: "Flows" },
  { href: "/torcs", label: "TORCS" },
  { href: "/about", label: "About" },
];

export function Nav() {
  const path = usePathname();
  return (
    <nav className="fixed inset-x-0 bottom-6 z-50 flex justify-center pointer-events-none">
      <div className="liquid-pill pointer-events-auto flex items-center gap-1 p-1.5 text-sm">
        {links.map((l) => {
          const active = path === l.href || (l.href !== "/" && path?.startsWith(l.href));
          return (
            <Link
              key={l.href}
              href={l.href}
              className={cn(
                "rounded-full px-4 py-1.5 transition-all duration-300 ease-spring",
                active ? "bg-white/[0.10] text-ink" : "text-ink-dim hover:text-ink hover:bg-white/[0.05]"
              )}
            >
              {l.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
