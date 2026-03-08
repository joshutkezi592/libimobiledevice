import SocialLinks from "./SocialLinks";

export default function Footer() {
  const year = new Date().getFullYear();

  const links = [
    { href: "#music", label: "Music" },
    { href: "#about", label: "About" },
    { href: "#downloads", label: "Downloads" },
    { href: "#contact", label: "Contact" },
  ];

  return (
    <footer className="relative py-14 px-6 bg-black border-t border-white/5">
      <div className="max-w-6xl mx-auto">
        {/* Top section */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-8 mb-10">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full border border-cyan-400/40 flex items-center justify-center">
              <div className="w-2 h-2 rounded-full bg-cyan-400/70" />
            </div>
            <span
              className="text-sm font-bold tracking-[0.25em] uppercase text-white"
              style={{ fontFamily: "'Orbitron', sans-serif" }}
            >
              DJ Sonu
            </span>
          </div>

          {/* Footer nav */}
          <nav>
            <ul className="flex items-center gap-8">
              {links.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-[11px] text-gray-600 hover:text-cyan-400 tracking-[0.2em] uppercase transition-colors"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>

          {/* Socials */}
          <SocialLinks />
        </div>

        {/* Divider */}
        <div className="section-divider mb-8" />

        {/* Bottom */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-[11px] text-gray-700 tracking-wider">
            &copy; {year} DJ Sonu. All rights reserved.
          </p>
          <p className="text-[11px] text-gray-800 tracking-wider">
            Crafted with passion
          </p>
        </div>
      </div>
    </footer>
  );
}
