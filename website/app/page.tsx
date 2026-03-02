import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import About from "./components/About";
import Mixes from "./components/Mixes";
import Contact from "./components/Contact";
import Footer from "./components/Footer";

export default function Home() {
  return (
    <main>
      <Navbar />
      <Hero />
      <About />
      <Mixes />
      <Contact />
      <Footer />
    </main>
  );
}
