/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['@ceo-os/ui', '@ceo-os/core'],
  output: 'standalone',
};
module.exports = nextConfig;
