/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

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
}

module.exports = nextConfig
