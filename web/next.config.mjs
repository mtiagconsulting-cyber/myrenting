/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',            // exportación estática → SEO perfecto, hospedable en cualquier sitio
  images: { unoptimized: true },
  trailingSlash: true,
};
export default nextConfig;
