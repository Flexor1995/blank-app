/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  // Garantir que funcione em diferentes ambientes
  hostname: '0.0.0.0',
  port: 3000,
}

module.exports = nextConfig