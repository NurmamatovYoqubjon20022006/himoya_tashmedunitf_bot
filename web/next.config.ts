import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    serverComponentsHmrCache: true,
  },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "api.telegram.org" },
    ],
  },
};

export default nextConfig;
