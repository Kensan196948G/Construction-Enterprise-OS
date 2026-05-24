/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['@construction-enterprise-os/ui', '@construction-enterprise-os/core'],
  output: 'standalone',
};
module.exports = nextConfig;
