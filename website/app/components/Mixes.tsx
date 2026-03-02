// TODO: Replace these placeholder video IDs with DJ Sonu's actual YouTube video IDs.
// Find video IDs in the URL: youtube.com/watch?v=<VIDEO_ID>
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
];

export default function Mixes() {
  return (
    <section id="mixes" className="py-24 px-6 bg-[#050505]">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-14">
          <span className="text-xs tracking-[0.4em] text-purple-400 uppercase font-medium">
            Latest Mixes
          </span>
          <h2 className="mt-3 text-4xl sm:text-5xl font-bold text-white">
            Feel the Music
          </h2>
          <p className="mt-4 text-gray-500 max-w-md mx-auto">
            Handcrafted mixes across genres — from deep house to high-energy
            EDM. New mixes dropped regularly.
          </p>
        </div>

        {/* Mix cards */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {mixes.map((mix, index) => (
            <div
              key={index}
              className="group rounded-2xl overflow-hidden border border-white/10 bg-white/[0.02] hover:border-purple-500/40 transition-all duration-300"
            >
              {/* YouTube thumbnail */}
              <div className="relative aspect-video bg-black overflow-hidden">
                <img
                  src={`https://img.youtube.com/vi/${mix.id}/hqdefault.jpg`}
                  alt={mix.title}
                  className="w-full h-full object-cover opacity-70 group-hover:opacity-90 transition-opacity duration-300"
                />
                {/* Play overlay */}
                <a
                  href={`https://www.youtube.com/watch?v=${mix.id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="absolute inset-0 flex items-center justify-center"
                  aria-label={`Play ${mix.title}`}
                >
                  <div className="w-14 h-14 rounded-full bg-white/10 backdrop-blur-sm border border-white/30 flex items-center justify-center group-hover:bg-purple-600/80 transition-colors duration-300">
                    <svg
                      className="w-6 h-6 text-white ml-1"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M8 5v14l11-7z" />
                    </svg>
                  </div>
                </a>
                {/* Genre badge */}
                <span className="absolute top-3 right-3 text-xs bg-black/70 text-purple-300 px-3 py-1 rounded-full tracking-wider">
                  {mix.genre}
                </span>
              </div>

              <div className="p-5">
                <h3 className="text-white font-semibold text-sm tracking-wide">
                  {mix.title}
                </h3>
                <a
                  href="https://www.youtube.com/@djaysonu"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-2 inline-block text-xs text-gray-500 hover:text-purple-400 transition-colors tracking-wider"
                >
                  Watch on YouTube →
                </a>
              </div>
            </div>
          ))}
        </div>

        {/* CTA to channel */}
        <div className="text-center mt-12">
          <a
            href="https://www.youtube.com/@djaysonu"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-8 py-3 border border-white/20 rounded-full text-sm text-white tracking-wider uppercase hover:bg-white/5 hover:border-white/40 transition-all duration-200"
          >
            <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 24 24">
              <path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
            </svg>
            View All Mixes on YouTube
          </a>
        </div>
      </div>
    </section>
  );
}
