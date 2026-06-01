/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ["three"],
  async rewrites() {
    const backend = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";
    return [
      { source: "/api/backend/:path*", destination: `${backend}/:path*` },
    ];
  },
};
export default nextConfig;
