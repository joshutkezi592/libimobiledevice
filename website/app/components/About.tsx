export default function About() {
  const stats = [
    { value: "5+", label: "Years Experience" },
    { value: "100+", label: "Mixes Published" },
    { value: "10K+", label: "YouTube Subscribers" },
  ];

  return (
    <section id="about" className="py-24 px-6 bg-black">
      <div className="max-w-4xl mx-auto">
        <div className="grid md:grid-cols-2 gap-16 items-center">
          {/* Text */}
          <div>
            <span className="text-xs tracking-[0.4em] text-purple-400 uppercase font-medium">
              About Me
            </span>
            <h2 className="mt-3 text-4xl sm:text-5xl font-bold text-white leading-tight">
              The Sound Behind
              <br />
              the Moment
            </h2>
            <p className="mt-6 text-gray-400 leading-relaxed">
              Hey, I&apos;m <strong className="text-white">DJ Sonu</strong> — a
              professional DJ and mix artist passionate about creating
              experiences through music. From high-energy festival sets to
              smooth late-night grooves, I craft mixes that connect people.
            </p>
            <p className="mt-4 text-gray-400 leading-relaxed">
              I regularly upload my mixes to YouTube, blending genres to keep
              the vibe fresh. Whether you need a DJ for your event or just want
              to enjoy some great music, you&apos;re in the right place.
            </p>
            <a
              href="https://www.youtube.com/@djaysonu"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block mt-8 text-sm text-purple-400 hover:text-purple-300 tracking-wider uppercase underline underline-offset-4 transition-colors"
            >
              Follow on YouTube →
            </a>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 gap-6">
            {stats.map((stat) => (
              <div
                key={stat.label}
                className="border border-white/10 rounded-2xl px-8 py-6 bg-white/[0.02] hover:bg-white/[0.04] transition-colors"
              >
                <div className="text-4xl font-black text-white">{stat.value}</div>
                <div className="mt-1 text-sm text-gray-500 tracking-wider uppercase">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
