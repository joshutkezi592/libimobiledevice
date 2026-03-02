import SocialLinks from "./SocialLinks";

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="py-10 px-6 bg-[#050505] border-t border-white/5">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <p className="text-sm text-gray-600">
          © {year}{" "}
          <span className="text-gray-500 font-medium">DJ Sonu</span>. All
          rights reserved.
        </p>
        <SocialLinks />
      </div>
    </footer>
  );
}
