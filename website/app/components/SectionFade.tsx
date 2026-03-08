"use client";

import { useRef, ReactNode } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

interface SectionFadeProps {
  children: ReactNode;
  className?: string;
}

export default function SectionFade({ children, className = "" }: SectionFadeProps) {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  // Fade in as section scrolls into view, stay visible, fade out as it exits
  const opacity = useTransform(
    scrollYProgress,
    [0, 0.15, 0.85, 1],
    [0, 1, 1, 0]
  );

  // Subtle vertical shift for parallax depth
  const y = useTransform(
    scrollYProgress,
    [0, 0.15, 0.85, 1],
    [60, 0, 0, -60]
  );

  // Slight scale for cinematic feel
  const scale = useTransform(
    scrollYProgress,
    [0, 0.15, 0.85, 1],
    [0.97, 1, 1, 0.97]
  );

  return (
    <motion.div
      ref={ref}
      style={{ opacity, y, scale }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
