/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  transpilePackages: ['@ceo-os/ui', '@ceo-os/core'],
};
const withPWA = nextConfig; // PWA will be added via next-pwa later
module.exports = nextConfig;
