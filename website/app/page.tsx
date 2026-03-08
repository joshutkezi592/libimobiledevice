import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import Mixes from "./components/Mixes";
import About from "./components/About";
import Downloads from "./components/Downloads";
import Contact from "./components/Contact";
import Footer from "./components/Footer";
import ParticleBackground from "./components/ParticleBackground";
import SectionFade from "./components/SectionFade";

export default function Home() {
  return (
    <main>
      <ParticleBackground />
      <Navbar />
      <Hero />
      <SectionFade>
        <Mixes />
      </SectionFade>
      <SectionFade>
        <About />
      </SectionFade>
      <SectionFade>
        <Downloads />
      </SectionFade>
      <SectionFade>
        <Contact />
      </SectionFade>
      <SectionFade>
        <Footer />
      </SectionFade>
    </main>
  );
}
