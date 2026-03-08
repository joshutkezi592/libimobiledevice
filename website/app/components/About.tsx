"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import ScrollReveal from "./ScrollReveal";

export default function About() {
  const sectionRef = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"],
  });

  const imgY = useTransform(scrollYProgress, [0, 1], [60, -60]);
  const imgRotateY = useTransform(scrollYProgress, [0, 0.5, 1], [-8, 0, 8]);
  const imgScale = useTransform(scrollYProgress, [0, 0.5, 1], [0.95, 1.02, 0.95]);
  const textRotateX = useTransform(scrollYProgress, [0, 0.5, 1], [5, 0, -5]);

  const stats = [
    { value: "5+", label: "Years Active" },
    { value: "100+", label: "Tracks Released" },
    { value: "10K+", label: "Subscribers" },
    { value: "50+", label: "Live Shows" },
  ];

  return (
    <section
      ref={sectionRef}
      id="about"
      className="relative py-28 px-6 bg-black overflow-hidden"
    >
      {/* Background accent */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-cyan-500/5 rounded-full blur-[150px] pointer-events-none" />

      <div className="max-w-6xl mx-auto relative z-10">
        <div className="grid lg:grid-cols-2 gap-20 items-center">
          {/* 3D Artist Image */}
          <ScrollReveal direction="left">
            <div className="perspective-container">
              <motion.div
                className="relative preserve-3d"
                style={{
                  y: imgY,
                  rotateY: imgRotateY,
                  scale: imgScale,
                  transformPerspective: 1000,
                }}
              >
                <div className="aspect-[3/4] max-w-md mx-auto rounded-2xl overflow-hidden depth-shadow">
                  {/* Artist image */}
                  <img
                    src="/artist.jpg"
                    alt="DJ Sonu"
                    className="w-full h-full object-cover"
                  />
                  {/* Overlay gradient */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-cyan-900/20" />
                  {/* Glow border on hover */}
                  <div className="absolute inset-0 rounded-2xl border border-cyan-400/0 hover:border-cyan-400/20 transition-colors duration-500" />
                  {/* Bottom text overlay */}
                  <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/90 to-transparent">
                    <p
                      className="text-lg font-bold text-white tracking-wider"
                      style={{ fontFamily: "'Orbitron', sans-serif" }}
                    >
                      DJ SONU
                    </p>
                    <p className="text-xs text-cyan-400/70 tracking-[0.2em] uppercase mt-1">
                      Professional DJ &amp; Producer
                    </p>
                  </div>
                </div>
                {/* Decorative 3D corner accents */}
                <div
                  className="absolute -top-4 -left-4 w-16 h-16 border-t-2 border-l-2 border-cyan-400/20 rounded-tl-lg"
                  style={{ transform: "translateZ(20px)" }}
                />
                <div
                  className="absolute -bottom-4 -right-4 w-16 h-16 border-b-2 border-r-2 border-cyan-400/20 rounded-br-lg"
                  style={{ transform: "translateZ(20px)" }}
                />
              </motion.div>
            </div>
          </ScrollReveal>

          {/* Text content with 3D scroll */}
          <div className="perspective-container">
            <motion.div
              style={{ rotateX: textRotateX, transformPerspective: 800 }}
            >
              <ScrollReveal direction="right" delay={0.2}>
                <div>
                  <span className="text-xs tracking-[0.4em] text-cyan-400/80 uppercase font-medium">
                    About
                  </span>
                  <h2
                    className="mt-3 text-4xl sm:text-5xl font-bold text-white leading-tight"
                    style={{ fontFamily: "'Orbitron', sans-serif" }}
                  >
                    The Vision Behind
                    <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
                      The Sound
                    </span>
                  </h2>
                  <p className="mt-6 text-gray-400 leading-relaxed text-[15px]">
                    I&apos;m{" "}
                    <strong className="text-white">DJ Sonu</strong> — a
                    professional DJ and music producer dedicated to creating
                    immersive sonic experiences. From pulsating festival stages
                    to intimate underground sets, every performance is a
                    journey.
                  </p>
                  <p className="mt-4 text-gray-400 leading-relaxed text-[15px]">
                    Blending electronic, house, and experimental sounds, I push
                    the boundaries of what&apos;s possible behind the decks.
                    Each mix and production is crafted to connect, inspire, and
                    move.
                  </p>

                  {/* Stats grid with 3D hover */}
                  <div className="grid grid-cols-2 gap-4 mt-10">
                    {stats.map((stat) => (
                      <div
                        key={stat.label}
                        className="glass-card card-3d rounded-xl px-5 py-4 cursor-default"
                      >
                        <div
                          className="text-3xl font-black text-cyan-400"
                          style={{ fontFamily: "'Orbitron', sans-serif" }}
                        >
                          {stat.value}
                        </div>
                        <div className="mt-1 text-[11px] text-gray-500 tracking-[0.15em] uppercase">
                          {stat.label}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </ScrollReveal>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Section divider */}
      <div className="section-divider absolute bottom-0 left-0 right-0" />
    </section>
  );
}
