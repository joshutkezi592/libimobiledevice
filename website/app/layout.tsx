import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DJ Sonu — Professional DJ & Music Producer",
  description:
    "DJ Sonu is a professional DJ and music producer creating unforgettable experiences. Explore music, tour dates, and book for events.",
  openGraph: {
    title: "DJ Sonu — Professional DJ & Music Producer",
    description:
      "Crafting unforgettable sonic experiences. Explore music, tour dates, and book DJ Sonu for your next event.",
    url: "https://www.youtube.com/@djaysonu",
    siteName: "DJ Sonu",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Orbitron:wght@400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased bg-black text-white">
        {children}
      </body>
    </html>
  );
}
