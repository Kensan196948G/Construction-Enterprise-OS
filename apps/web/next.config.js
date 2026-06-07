/** @type {import('next').NextConfig} */
// API_GATEWAY (no NEXT_PUBLIC_ prefix) is server-side only — can be overridden at runtime in Docker
const API_GATEWAY =
  process.env.API_GATEWAY ??
  process.env.NEXT_PUBLIC_API_GATEWAY ??
  "http://localhost:9000";

const nextConfig = {
  transpilePackages: [
    "@construction-enterprise-os/ui",
    "@construction-enterprise-os/core",
  ],
  output: "standalone",
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${API_GATEWAY}/api/v1/:path*`,
      },
    ];
  },
};
module.exports = nextConfig;
