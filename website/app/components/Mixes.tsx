"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import ScrollReveal from "./ScrollReveal";

// TODO: Replace these placeholder video IDs with DJ Sonu's actual YouTube video IDs.
const mixes = [
  {
    id: "REPLACE_WITH_VIDEO_ID_1",
    title: "Deep House Mix Vol. 1",
    genre: "Deep House",
  },
  {
    id: "REPLACE_WITH_VIDEO_ID_2",
    title: "EDM Festival Mix 2024",
    genre: "EDM",
  },
  {
    id: "REPLACE_WITH_VIDEO_ID_3",
    title: "Late Night Vibes Mix",
    genre: "Chill / Lo-Fi",
  },
  {
    id: "REPLACE_WITH_VIDEO_ID_4",
    title: "Bass Drop Sessions",
    genre: "Bass House",
  },
];

function MixCard3D({
  mix,
  index,
}: {
  mix: (typeof mixes)[0];
  index: number;
}) {
  const cardRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const card = cardRef.current;
    if (!card) return;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const rotateX = ((y - centerY) / centerY) * -8;
    const rotateY = ((x - centerX) / centerX) * 8;
    card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
  };

  const handleMouseLeave = () => {
    const card = cardRef.current;
    if (!card) return;
    card.style.transform =
      "perspective(800px) rotateX(0deg) rotateY(0deg) scale(1)";
  };

  return (
    <ScrollReveal delay={index * 0.1}>
      <div
        ref={cardRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        className="group glass-card rounded-2xl overflow-hidden hover:border-cyan-400/20 transition-[border-color,box-shadow] duration-500 cursor-pointer depth-shadow"
        style={{
          transformStyle: "preserve-3d",
          transition: "transform 0.15s ease-out, border-color 0.5s, box-shadow 0.5s",
        }}
      >
        {/* YouTube thumbnail */}
        <div className="relative aspect-video bg-black overflow-hidden">
          <img
            src={`https://img.youtube.com/vi/${mix.id}/hqdefault.jpg`}
            alt={mix.title}
            className="w-full h-full object-cover opacity-60 group-hover:opacity-80 group-hover:scale-110 transition-all duration-700"
          />
          {/* Gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
          {/* Play button — pops forward in 3D */}
          <a
            href={`https://www.youtube.com/watch?v=${mix.id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="absolute inset-0 flex items-center justify-center"
            aria-label={`Play ${mix.title}`}
          >
            <div
              className="w-16 h-16 rounded-full bg-white/5 backdrop-blur-md border border-white/20 flex items-center justify-center group-hover:bg-cyan-500/20 group-hover:border-cyan-400/50 group-hover:scale-110 transition-all duration-500"
              style={{ transform: "translateZ(40px)" }}
            >
              <svg
                className="w-6 h-6 text-white ml-0.5"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M8 5v14l11-7z" />
              </svg>
            </div>
          </a>
          {/* Genre badge */}
          <span className="absolute top-4 right-4 text-[10px] bg-black/60 backdrop-blur-sm text-cyan-300 px-3 py-1 rounded-full tracking-[0.15em] uppercase border border-cyan-400/10">
            {mix.genre}
          </span>
        </div>

        <div className="p-5" style={{ transform: "translateZ(20px)" }}>
          <h3 className="text-white font-semibold text-sm tracking-wide group-hover:text-cyan-400 transition-colors">
            {mix.title}
          </h3>
          <a
            href="https://www.youtube.com/@djaysonu"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 inline-block text-[11px] text-gray-600 hover:text-cyan-400 transition-colors tracking-[0.15em] uppercase"
          >
            Listen Now →
          </a>
        </div>
      </div>
    </ScrollReveal>
  );
}

export default function Mixes() {
  const sectionRef = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"],
  });

  const sectionRotateX = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [6, 0, 0, -6]);
  const sectionScale = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0.96, 1, 1, 0.96]);

  return (
    <section
      ref={sectionRef}
      id="music"
      className="relative py-28 px-6 bg-black overflow-hidden"
    >
      {/* Background */}
      <div className="absolute top-1/2 left-0 w-[400px] h-[400px] bg-blue-600/5 rounded-full blur-[150px] pointer-events-none" />

      <motion.div
        className="max-w-6xl mx-auto relative z-10"
        style={{
          rotateX: sectionRotateX,
          scale: sectionScale,
          transformPerspective: 1200,
        }}
      >
        {/* Header */}
        <ScrollReveal>
          <div className="text-center mb-16">
            <span className="text-xs tracking-[0.4em] text-cyan-400/80 uppercase font-medium">
              Releases
            </span>
            <h2
              className="mt-3 text-4xl sm:text-5xl font-bold text-white"
              style={{ fontFamily: "'Orbitron', sans-serif" }}
            >
              Music
            </h2>
            <p className="mt-4 text-gray-500 max-w-md mx-auto text-sm">
              Handcrafted mixes and original productions. New releases dropped
              regularly.
            </p>
          </div>
        </ScrollReveal>

        {/* Mix grid */}
        <div className="grid sm:grid-cols-2 gap-6" style={{ perspective: "1000px" }}>
          {mixes.map((mix, index) => (
            <MixCard3D key={index} mix={mix} index={index} />
          ))}
        </div>

        {/* CTA to channel */}
        <ScrollReveal delay={0.3}>
          <div className="text-center mt-14">
            <a
              href="https://www.youtube.com/@djaysonu"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-3 px-8 py-3 border border-white/10 rounded-full text-xs text-white tracking-[0.15em] uppercase hover:border-cyan-400/40 hover:text-cyan-400 transition-all duration-300"
            >
              <svg
                className="w-4 h-4 text-red-500"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
              </svg>
              View All on YouTube
            </a>
          </div>
        </ScrollReveal>
      </motion.div>

      {/* Section divider */}
      <div className="section-divider absolute bottom-0 left-0 right-0" />
    </section>
  );
}
