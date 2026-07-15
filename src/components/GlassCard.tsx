import type { ReactNode, HTMLAttributes } from "react";
import { useTilt } from "@/hooks/useTilt";
import { cn } from "@/lib/utils";

interface GlassCardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  /** Enable mouse-tracked 3D tilt. Default: true */
  tilt?: boolean;
  /** Max tilt angle in degrees. Default: 6 */
  maxTilt?: number;
  /** Visual variant: "default" | "subtle" | "stat" */
  variant?: "default" | "subtle" | "stat";
  /** Enable parallax float on inner .glass-parallax children */
  parallax?: boolean;
}

/**
 * GlassCard — primary 3D glassmorphic surface with mouse-tracked
 * perspective tilt, layered specular highlights, rim light, and
 * ambient occlusion. All visual depth is provided by index.css.
 */
export function GlassCard({
  children,
  className,
  tilt = true,
  maxTilt = 6,
  variant = "default",
  parallax = false,
  ...rest
}: GlassCardProps) {
  const { setTiltRef, onMouseMove, onMouseLeave } = useTilt<HTMLDivElement>(maxTilt);

  const variantClass =
    variant === "subtle"
      ? "glass-3d-subtle"
      : variant === "stat"
      ? "glass-3d-stat"
      : "glass-3d";

  return (
    <div
      ref={setTiltRef}
      className={cn(
        variantClass,
        tilt && "glass-tilt",
        parallax && "[transform-style:preserve-3d]",
        className
      )}
      onMouseMove={tilt ? onMouseMove : undefined}
      onMouseLeave={tilt ? onMouseLeave : undefined}
      {...rest}
    >
      {parallax ? <div className="glass-content">{children}</div> : children}
    </div>
  );
}
