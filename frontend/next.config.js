/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Don't use static export - use standalone server for dynamic routes
  // output: 'export',

  // Disable webpack caching in dev to prevent corruption
  webpack: (config, { dev }) => {
    if (dev) {
      config.cache = false
    }
    return config
  },

  // Optimize for stability
  onDemandEntries: {
    maxInactiveAge: 60 * 1000,
    pagesBufferLength: 2,
  },

  // Force rebuild: 2026-03-05
  generateBuildId: async () => {
    return `build-${Date.now()}`
  },
}

module.exports = nextConfig
