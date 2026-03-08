"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import SocialLinks from "./SocialLinks";

export default function Hero() {
  const sectionRef = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end start"],
  });

  // Parallax: image moves slower, content moves faster + scales
  const imgY = useTransform(scrollYProgress, [0, 1], ["0%", "30%"]);
  const imgScale = useTransform(scrollYProgress, [0, 1], [1, 1.15]);
  const contentY = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
  const contentOpacity = useTransform(scrollYProgress, [0, 0.6], [1, 0]);
  const rotateX = useTransform(scrollYProgress, [0, 1], [0, 15]);
  // Entire section fades out as you scroll past it
  const sectionOpacity = useTransform(scrollYProgress, [0, 0.7, 1], [1, 1, 0]);

  return (
    <motion.section
      ref={sectionRef}
      id="hero"
      style={{ opacity: sectionOpacity }}
      className="relative min-h-screen flex flex-col items-center justify-center text-center overflow-hidden bg-black"
    >
      {/* ── Artist Background Image with 3D Parallax ── */}
      <motion.div
        className="absolute inset-0 z-0"
        style={{ y: imgY, scale: imgScale }}
      >
        <div
          className="absolute inset-[-15%] bg-cover bg-center bg-no-repeat"
          style={{ backgroundImage: "url('/artist.jpg')" }}
        />
        {/* Dark overlays for readability */}
        <div className="absolute inset-0 bg-black/50" />
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-transparent to-black" />
        {/* Cyan tint overlay */}
        <div className="absolute inset-0 bg-cyan-900/10 mix-blend-overlay" />
      </motion.div>

      {/* ── Grid overlay ── */}
      <div className="absolute inset-0 z-[1] pointer-events-none">
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(0,212,255,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.3) 1px, transparent 1px)",
            backgroundSize: "60px 60px",
          }}
        />
        {/* Vignette */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_0%,rgba(0,0,0,0.5)_100%)]" />
      </div>

      {/* ── 3D Foreground Content ── */}
      <motion.div
        className="relative z-10 flex flex-col items-center gap-6 max-w-4xl px-6 preserve-3d"
        style={{
          y: contentY,
          opacity: contentOpacity,
          rotateX,
          transformPerspective: 1200,
        }}
      >
        {/* Animated label */}
        <motion.span
          initial={{ opacity: 0, y: 30, rotateX: -20 }}
          animate={{ opacity: 1, y: 0, rotateX: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-xs tracking-[0.5em] text-cyan-400/80 uppercase font-medium"
        >
          DJ &bull; Producer &bull; Artist
        </motion.span>

        {/* Name with 3D depth */}
        <motion.h1
          initial={{ opacity: 0, scale: 0.8, rotateX: -30 }}
          animate={{ opacity: 1, scale: 1, rotateX: 0 }}
          transition={{ duration: 1.2, delay: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
          className="text-7xl sm:text-9xl font-black tracking-tight text-white leading-none text-glow"
          style={{ fontFamily: "'Orbitron', sans-serif", transformStyle: "preserve-3d" }}
        >
          <motion.span
            className="inline-block"
            style={{ transform: "translateZ(40px)" }}
          >
            DJ{" "}
          </motion.span>
          <motion.span
            className="inline-block text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-500 animate-gradient"
            style={{ transform: "translateZ(60px)" }}
          >
            SONU
          </motion.span>
        </motion.h1>

        {/* Tagline */}
        <motion.p
          initial={{ opacity: 0, y: 30, rotateX: -15 }}
          animate={{ opacity: 1, y: 0, rotateX: 0 }}
          transition={{ duration: 0.8, delay: 0.7 }}
          className="text-gray-300 text-lg sm:text-xl max-w-lg leading-relaxed"
        >
          Crafting immersive sonic experiences that transcend boundaries. From
          the studio to the stage.
        </motion.p>

        {/* CTA buttons */}
        <motion.div
          initial={{ opacity: 0, y: 30, rotateX: -10 }}
          animate={{ opacity: 1, y: 0, rotateX: 0 }}
          transition={{ duration: 0.8, delay: 0.9 }}
          className="flex flex-wrap items-center justify-center gap-4 mt-2"
        >
          <a
            href="https://www.youtube.com/@djaysonu"
            target="_blank"
            rel="noopener noreferrer"
            className="group relative px-8 py-3 bg-cyan-500 text-black text-sm font-bold tracking-[0.15em] uppercase rounded-full overflow-hidden transition-all duration-300 hover:shadow-[0_0_40px_rgba(0,212,255,0.5)] hover:scale-105"
          >
            <span className="relative z-10">Explore Music</span>
          </a>
          {/* <button
            onClick={() => {
              const el = document.querySelector("#events");
              if (el) el.scrollIntoView({ behavior: "smooth" });
            }}
            className="px-8 py-3 border border-white/20 text-white text-sm font-semibold tracking-[0.15em] uppercase rounded-full hover:border-cyan-400/50 hover:text-cyan-400 hover:scale-105 transition-all duration-300"
          >
            Tour Dates
          </button> */}
        </motion.div>

        {/* Social links */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 1.2 }}
          className="mt-6"
        >
          <SocialLinks />
        </motion.div>
      </motion.div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 1.5 }}
        className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 z-10"
      >
        <span className="text-[10px] text-gray-500 tracking-[0.3em] uppercase">
          Scroll
        </span>
        <div className="w-5 h-8 rounded-full border border-gray-600 flex items-start justify-center p-1">
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
            className="w-1 h-2 rounded-full bg-cyan-400/60"
          />
        </div>
      </motion.div>
    </motion.section>
  );
}
