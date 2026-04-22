import type { Metadata } from "next";
import { Plus_Jakarta_Sans, DM_Sans, Source_Serif_4 } from "next/font/google";
import "./globals.css";

const jakarta = Plus_Jakarta_Sans({
  variable: "--font-jakarta",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
});

const dm = DM_Sans({
  variable: "--font-dm",
  subsets: ["latin"],
  weight: ["400", "500"],
});

const sourceSerif = Source_Serif_4({
  variable: "--font-serif",
  subsets: ["latin"],
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "Carousel Generator — Clearer Thinking",
  description: "Generate Instagram carousels from Clearer Thinking blog posts",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${jakarta.variable} ${dm.variable} ${sourceSerif.variable} h-full`}>
      <body className="min-h-full flex flex-col antialiased">{children}</body>
    </html>
  );
}
