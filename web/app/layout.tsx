import type { Metadata, Viewport } from "next";
import "./globals.css";
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import { ThemeProvider } from "@/components/theme-provider";

export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_BASE_URL ?? "https://pulse-ai.app"
  ),
  title: "Pulse AI — Your AI news heartbeat",
  description:
    "The day's most important AI stories, curated and ranked. From 100+ trusted sources.",
  openGraph: {
    title: "Pulse AI — Your AI news heartbeat",
    description:
      "The day's most important AI stories, curated and ranked. From 100+ trusted sources.",
    images: ["/icons/og-image.png"],
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Pulse AI — Your AI news heartbeat",
    description:
      "The day's most important AI stories, curated and ranked. From 100+ trusted sources.",
    images: ["/icons/og-image.png"],
  },
  icons: {
    icon: [
      { url: "/icons/favicon-16x16.png", sizes: "16x16", type: "image/png" },
      { url: "/icons/favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/icons/favicon-48x48.png", sizes: "48x48", type: "image/png" },
    ],
    apple: [
      {
        url: "/icons/apple-touch-icon.png",
        sizes: "180x180",
        type: "image/png",
      },
    ],
  },
  manifest: "/manifest.webmanifest",
};

export const viewport: Viewport = {
  themeColor: "#4F46E5",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="font-sans antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
