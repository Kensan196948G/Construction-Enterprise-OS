/** @type {import('next').NextConfig} */
const API_GATEWAY =
  process.env.NEXT_PUBLIC_API_GATEWAY ?? "http://localhost:9000";

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
