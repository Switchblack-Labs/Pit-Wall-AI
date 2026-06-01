import { cn } from "@/lib/utils";

export function Bezel({
  className,
  innerClassName,
  children,
}: {
  className?: string;
  innerClassName?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={cn("bezel-shell", className)}>
      <div className={cn("bezel-core p-6", innerClassName)}>{children}</div>
    </div>
  );
}

export function Eyebrow({ children, className }: { children: React.ReactNode; className?: string }) {
  return <span className={cn("eyebrow", className)}>{children}</span>;
}
