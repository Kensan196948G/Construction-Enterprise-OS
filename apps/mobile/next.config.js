/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  transpilePackages: ['@construction-enterprise-os/ui', '@construction-enterprise-os/core'],
};
const withPWA = nextConfig; // PWA will be added via next-pwa later
module.exports = nextConfig;
