"use client";

import SocialLinks from "./SocialLinks";

export default function Hero() {
  return (
    <section
      id="hero"
      className="relative min-h-screen flex flex-col items-center justify-center text-center px-6 overflow-hidden bg-black"
    >
      {/* Background gradient orbs */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-purple-600/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 left-1/2 -translate-x-1/2 w-[400px] h-[400px] bg-indigo-600/15 rounded-full blur-[100px]" />
      </div>

      <div className="relative z-10 flex flex-col items-center gap-6">
        {/* Label */}
        <span className="text-xs tracking-[0.4em] text-purple-400 uppercase font-medium">
          Professional DJ &amp; Mix Artist
        </span>

        {/* Name */}
        <h1 className="text-6xl sm:text-8xl font-black tracking-tight text-white leading-none">
          DJ{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-indigo-400">
            Sonu
          </span>
        </h1>

        {/* Tagline */}
        <p className="text-gray-400 text-lg sm:text-xl max-w-md leading-relaxed">
          Crafting unforgettable mixes that move the crowd. From the decks to
          your ears.
        </p>

        {/* CTA buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 mt-2">
          <a
            href="https://www.youtube.com/@djaysonu"
            target="_blank"
            rel="noopener noreferrer"
            className="px-7 py-3 bg-white text-black text-sm font-semibold tracking-wider uppercase rounded-full hover:bg-gray-100 transition-colors duration-200"
          >
            Watch Mixes
          </a>
          <button
            onClick={() => {
              const el = document.querySelector("#contact");
              if (el) el.scrollIntoView({ behavior: "smooth" });
            }}
            className="px-7 py-3 border border-white/30 text-white text-sm font-semibold tracking-wider uppercase rounded-full hover:border-white/70 hover:bg-white/5 transition-all duration-200"
          >
            Book Now
          </button>
        </div>

        {/* Social links */}
        <div className="mt-4">
          <SocialLinks />
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 animate-bounce">
        <span className="text-xs text-gray-600 tracking-widest uppercase">Scroll</span>
        <svg
          className="w-4 h-4 text-gray-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </section>
  );
}
