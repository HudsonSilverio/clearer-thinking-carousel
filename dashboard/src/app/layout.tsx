import type { Metadata } from "next";
import {
  Plus_Jakarta_Sans, DM_Sans, Source_Serif_4,
  Inter, Lora, Merriweather, Roboto, Open_Sans,
} from "next/font/google";
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

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

const lora = Lora({
  variable: "--font-lora",
  subsets: ["latin"],
  weight: ["400", "500"],
});

const merriweather = Merriweather({
  variable: "--font-merriweather",
  subsets: ["latin"],
  weight: ["400", "700"],
});

const roboto = Roboto({
  variable: "--font-roboto",
  subsets: ["latin"],
  weight: ["400", "500"],
});

const openSans = Open_Sans({
  variable: "--font-opensans",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Carousel Generator — Clearer Thinking",
  description: "Generate Instagram carousels from Clearer Thinking blog posts",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const fonts = [
    jakarta.variable, dm.variable, sourceSerif.variable,
    inter.variable, lora.variable, merriweather.variable,
    roboto.variable, openSans.variable,
  ].join(" ");
  return (
    <html lang="en" className={`${fonts} h-full`} suppressHydrationWarning={true}>
      <body className="min-h-full flex flex-col antialiased" suppressHydrationWarning={true}>{children}</body>
    </html>
  );
}
