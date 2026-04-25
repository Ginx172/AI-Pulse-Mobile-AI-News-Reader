import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Pulse AI",
    short_name: "Pulse AI",
    description: "Your AI news heartbeat",
    start_url: "/",
    display: "standalone",
    background_color: "#000000",
    theme_color: "#4F46E5",
    orientation: "portrait",
    icons: [
      {
        src: "/icons/pwa-192x192.png",
        sizes: "192x192",
        type: "image/png",
        purpose: "any maskable",
      },
      {
        src: "/icons/pwa-512x512.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "any maskable",
      },
    ],
  };
}
