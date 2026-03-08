"use client";

import { useEffect, useState } from "react";
import ScrollReveal from "./ScrollReveal";

interface Track {
  name: string;
  filename: string;
  url: string;
  size: number;
  addedAt: number;
}

function formatSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function Downloads() {
  const [tracks, setTracks] = useState<Track[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/downloads")
      .then((res) => res.json())
      .then((data) => {
        setTracks(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <section
      id="downloads"
      className="relative py-28 px-6 bg-[#030303] overflow-hidden"
    >
      {/* Background */}
      <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-purple-600/5 rounded-full blur-[150px] pointer-events-none" />

      <div className="max-w-4xl mx-auto relative z-10">
        {/* Header */}
        <ScrollReveal>
          <div className="text-center mb-16">
            <span className="text-xs tracking-[0.4em] text-cyan-400/80 uppercase font-medium">
              Free Downloads
            </span>
            <h2
              className="mt-3 text-4xl sm:text-5xl font-bold text-white"
              style={{ fontFamily: "'Orbitron', sans-serif" }}
            >
              Get the Music
            </h2>
            <p className="mt-4 text-gray-500 max-w-md mx-auto text-sm">
              Download exclusive mixes and tracks for free. New uploads added
              regularly.
            </p>
          </div>
        </ScrollReveal>

        {/* Track list */}
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="w-8 h-8 border-2 border-cyan-400/30 border-t-cyan-400 rounded-full animate-spin" />
          </div>
        ) : tracks.length === 0 ? (
          <ScrollReveal>
            <div className="glass-card rounded-2xl p-12 text-center">
              <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-white/5 border border-white/10 flex items-center justify-center">
                <svg
                  className="w-7 h-7 text-gray-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
                  />
                </svg>
              </div>
              <p className="text-gray-500 text-sm">
                New tracks coming soon. Stay tuned!
              </p>
            </div>
          </ScrollReveal>
        ) : (
          <div className="flex flex-col gap-0">
            {tracks.map((track, i) => (
              <ScrollReveal key={track.filename} delay={i * 0.06}>
                <div className="group flex items-center gap-4 sm:gap-6 py-5 border-b border-white/5 hover:border-cyan-400/15 transition-colors duration-300">
                  {/* Track number */}
                  <span
                    className="flex-shrink-0 w-8 text-center text-sm font-bold text-gray-700 group-hover:text-cyan-400 transition-colors"
                    style={{ fontFamily: "'Orbitron', sans-serif" }}
                  >
                    {String(i + 1).padStart(2, "0")}
                  </span>

                  {/* Icon */}
                  <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-white/[0.03] border border-white/5 flex items-center justify-center group-hover:border-cyan-400/20 group-hover:bg-cyan-400/5 transition-all duration-300">
                    <svg
                      className="w-4 h-4 text-gray-500 group-hover:text-cyan-400 transition-colors"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2z"
                      />
                    </svg>
                  </div>

                  {/* Track info */}
                  <div className="flex-1 min-w-0">
                    <h3 className="text-white text-sm font-semibold tracking-wide truncate group-hover:text-cyan-400 transition-colors">
                      {track.name}
                    </h3>
                    <p className="text-[11px] text-gray-600 mt-0.5 tracking-wider">
                      MP3 &bull; {formatSize(track.size)}
                    </p>
                  </div>

                  {/* Download button */}
                  <a
                    href={track.url}
                    download={track.filename}
                    className="flex-shrink-0 inline-flex items-center gap-2 px-5 py-2.5 text-[10px] tracking-[0.2em] uppercase border border-white/10 rounded-full text-gray-400 hover:border-cyan-400/50 hover:text-cyan-400 hover:bg-cyan-400/5 transition-all duration-300"
                  >
                    <svg
                      className="w-3.5 h-3.5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                      />
                    </svg>
                    Download
                  </a>
                </div>
              </ScrollReveal>
            ))}
          </div>
        )}
      </div>

      {/* Section divider */}
      <div className="section-divider absolute bottom-0 left-0 right-0" />
    </section>
  );
}
