import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DJ Sonu — Professional DJ & Mix Artist",
  description:
    "DJ Sonu is a professional DJ and mix artist creating unforgettable mixes. Book for events, explore mixes on YouTube, and connect on social media.",
  openGraph: {
    title: "DJ Sonu — Professional DJ & Mix Artist",
    description:
      "Crafting unforgettable mixes that move the crowd. Explore mixes and book DJ Sonu for your next event.",
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
      <body className="antialiased bg-black text-white">
        {children}
      </body>
    </html>
  );
}
