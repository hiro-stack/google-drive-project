import type { NextConfig } from "next";

const withPWA = require("next-pwa")({
  dest: "public",
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development', // 開発時は無効化（デバッグしやすくするため）
});

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // PWA (next-pwa) との互換性のため、Turbopackは使用しない
  // turbopack: {},
  /* config options here */
};

export default withPWA(nextConfig);
