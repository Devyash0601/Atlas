import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ATLAS-EO | Earth Observation Science Laboratory",
  description: "Autonomous Trustworthy Laboratory for Earth Observation Science",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-[#0b0f19] text-gray-100 min-h-screen">
        {children}
      </body>
    </html>
  );
}
