import type { NextConfig } from "next";

const withPWA = require("next-pwa")({
  dest: "public",
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development', // 開発時は無効化（デバッグしやすくするため）
});

const nextConfig: NextConfig = {
  reactStrictMode: true,
  turbopack: {}, // Turbopackを明示的に有効化（Next.js 16対応）
  /* config options here */
};

export default withPWA(nextConfig);
