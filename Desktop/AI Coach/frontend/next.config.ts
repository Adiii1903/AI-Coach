import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow images from any origin in dev
  images: { unoptimized: true },
};

export default nextConfig;
