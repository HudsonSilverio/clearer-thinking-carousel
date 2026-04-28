import type { NextConfig } from "next";

const apiUrl = process.env.NEXT_PUBLIC_API_URL || "";
const remotePatterns: { protocol: "http" | "https"; hostname: string; port?: string }[] = [
  { protocol: "http", hostname: "localhost", port: "8000" },
];

if (apiUrl.startsWith("https://")) {
  try {
    const { hostname } = new URL(apiUrl);
    remotePatterns.push({ protocol: "https", hostname });
  } catch {}
}

const nextConfig: NextConfig = {
  images: { remotePatterns },
};

export default nextConfig;
