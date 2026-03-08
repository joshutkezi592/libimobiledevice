"use client";

import ScrollReveal from "./ScrollReveal";

const events = [
  {
    date: "MAR 15",
    year: "2026",
    venue: "Club Aura",
    city: "Mumbai, India",
    status: "upcoming" as const,
  },
  {
    date: "MAR 28",
    year: "2026",
    venue: "Skybar Lounge",
    city: "Delhi, India",
    status: "upcoming" as const,
  },
  {
    date: "APR 05",
    year: "2026",
    venue: "Neon Festival",
    city: "Goa, India",
    status: "upcoming" as const,
  },
  {
    date: "APR 19",
    year: "2026",
    venue: "Warehouse 23",
    city: "Bangalore, India",
    status: "upcoming" as const,
  },
  {
    date: "MAY 10",
    year: "2026",
    venue: "Echo Arena",
    city: "Hyderabad, India",
    status: "upcoming" as const,
  },
];

export default function Events() {
  return (
    <section id="events" className="relative py-28 px-6 bg-[#030303] overflow-hidden">
      {/* Background */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-cyan-500/5 rounded-full blur-[150px] pointer-events-none" />

      <div className="max-w-4xl mx-auto relative z-10">
        {/* Header */}
        <ScrollReveal>
          <div className="text-center mb-16">
            <span className="text-xs tracking-[0.4em] text-cyan-400/80 uppercase font-medium">
              Live Shows
            </span>
            <h2
              className="mt-3 text-4xl sm:text-5xl font-bold text-white"
              style={{ fontFamily: "'Orbitron', sans-serif" }}
            >
              Tour Dates
            </h2>
            <p className="mt-4 text-gray-500 max-w-md mx-auto text-sm">
              Catch DJ Sonu live. Experience the energy, the bass, the crowd.
            </p>
          </div>
        </ScrollReveal>

        {/* Event list */}
        <div className="flex flex-col gap-0">
          {events.map((event, i) => (
            <ScrollReveal key={i} delay={i * 0.08}>
              <div className="group flex items-center gap-6 sm:gap-10 py-6 border-b border-white/5 hover:border-cyan-400/20 transition-colors duration-300 cursor-pointer">
                {/* Date */}
                <div className="flex-shrink-0 w-20 text-center">
                  <div
                    className="text-2xl font-bold text-white group-hover:text-cyan-400 transition-colors"
                    style={{ fontFamily: "'Orbitron', sans-serif" }}
                  >
                    {event.date}
                  </div>
                  <div className="text-[10px] text-gray-600 tracking-[0.2em]">
                    {event.year}
                  </div>
                </div>

                {/* Divider */}
                <div className="w-px h-10 bg-white/10 group-hover:bg-cyan-400/30 transition-colors" />

                {/* Venue info */}
                <div className="flex-1">
                  <h3 className="text-white font-semibold text-sm sm:text-base tracking-wide group-hover:text-cyan-400 transition-colors">
                    {event.venue}
                  </h3>
                  <p className="text-gray-500 text-xs sm:text-sm mt-0.5">
                    {event.city}
                  </p>
                </div>

                {/* Status / Ticket button */}
                <div className="flex-shrink-0">
                  <span className="inline-block px-5 py-2 text-[10px] tracking-[0.2em] uppercase border border-white/10 rounded-full text-gray-400 group-hover:border-cyan-400/50 group-hover:text-cyan-400 transition-all duration-300">
                    Tickets
                  </span>
                </div>
              </div>
            </ScrollReveal>
          ))}
        </div>

        {/* Bottom CTA */}
        <ScrollReveal delay={0.4}>
          <div className="text-center mt-12">
            <button
              onClick={() => {
                const el = document.querySelector("#contact");
                if (el) el.scrollIntoView({ behavior: "smooth" });
              }}
              className="inline-flex items-center gap-2 text-xs text-gray-500 hover:text-cyan-400 tracking-[0.2em] uppercase transition-colors"
            >
              Book for private events →
            </button>
          </div>
        </ScrollReveal>
      </div>

      {/* Section divider */}
      <div className="section-divider absolute bottom-0 left-0 right-0" />
    </section>
  );
}
