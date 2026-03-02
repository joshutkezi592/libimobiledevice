"use client";

import { useState, FormEvent } from "react";

type FormState = {
  name: string;
  email: string;
  subject: string;
  message: string;
};

type Status = "idle" | "loading" | "success" | "error";

export default function Contact() {
  const [form, setForm] = useState<FormState>({
    name: "",
    email: "",
    subject: "",
    message: "",
  });
  const [status, setStatus] = useState<Status>("idle");

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setStatus("loading");

    // TODO: Replace this simulated submission with a real backend integration.
    // Options: Next.js API route (/app/api/contact/route.ts), Formspree, or EmailJS.
    await new Promise((res) => setTimeout(res, 1200));

    // Reset and show success
    setForm({ name: "", email: "", subject: "", message: "" });
    setStatus("success");

    setTimeout(() => setStatus("idle"), 5000);
  };

  const inputClass =
    "w-full bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-purple-500/60 focus:bg-white/[0.06] transition-all duration-200";

  return (
    <section id="contact" className="py-24 px-6 bg-black">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <span className="text-xs tracking-[0.4em] text-purple-400 uppercase font-medium">
            Get in Touch
          </span>
          <h2 className="mt-3 text-4xl sm:text-5xl font-bold text-white">
            Book DJ Sonu
          </h2>
          <p className="mt-4 text-gray-500">
            Looking for a DJ for your event, collaboration, or just want to say
            hi? Drop a message below.
          </p>
        </div>

        {/* Form */}
        <form
          onSubmit={handleSubmit}
          noValidate
          className="flex flex-col gap-4"
        >
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label htmlFor="name" className="sr-only">
                Name
              </label>
              <input
                id="name"
                name="name"
                type="text"
                required
                value={form.name}
                onChange={handleChange}
                placeholder="Your Name"
                className={inputClass}
              />
            </div>
            <div>
              <label htmlFor="email" className="sr-only">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={form.email}
                onChange={handleChange}
                placeholder="your@email.com"
                className={inputClass}
              />
            </div>
          </div>

          <div>
            <label htmlFor="subject" className="sr-only">
              Subject
            </label>
            <select
              id="subject"
              name="subject"
              required
              value={form.subject}
              onChange={handleChange}
              className={`${inputClass} ${form.subject === "" ? "text-gray-600" : "text-white"}`}
            >
              <option value="" disabled>
                Select a Subject
              </option>
              <option value="booking">Event Booking</option>
              <option value="collaboration">Collaboration</option>
              <option value="promo">Promotion</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label htmlFor="message" className="sr-only">
              Message
            </label>
            <textarea
              id="message"
              name="message"
              required
              rows={5}
              value={form.message}
              onChange={handleChange}
              placeholder="Tell me about your event, date, venue..."
              className={`${inputClass} resize-none`}
            />
          </div>

          <button
            type="submit"
            disabled={status === "loading"}
            className="mt-2 w-full py-4 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold text-sm tracking-widest uppercase transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {status === "loading" ? "Sending..." : "Send Message"}
          </button>

          {/* Status messages */}
          {status === "success" && (
            <div className="text-center text-sm text-emerald-400 py-2">
              ✓ Message sent! I&apos;ll get back to you soon.
            </div>
          )}
          {status === "error" && (
            <div className="text-center text-sm text-red-400 py-2">
              Something went wrong. Please try again.
            </div>
          )}
        </form>

        {/* Direct contact info */}
        <div className="mt-12 pt-10 border-t border-white/10 flex flex-wrap justify-center gap-8 text-sm text-gray-600">
          <a
            href="https://www.instagram.com/djay_sonu"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-purple-400 transition-colors"
          >
            @djay_sonu on Instagram
          </a>
          <a
            href="https://www.facebook.com/Djaysonuofficial"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-purple-400 transition-colors"
          >
            Djaysonuofficial on Facebook
          </a>
        </div>
      </div>
    </section>
  );
}
