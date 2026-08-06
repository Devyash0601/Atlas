import type { Metadata } from 'next';
import './globals.css';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import StatusBar from '@/components/StatusBar';

export const metadata: Metadata = {
  title: 'ATLAS-EO | Earth Observation Science Laboratory',
  description: 'Autonomous Trustworthy Laboratory for Earth Observation Science',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-[#0b0f19] text-slate-100 min-h-screen flex flex-col font-sans">
        <Header />
        <div className="flex-1 flex overflow-hidden">
          <Sidebar />
          <main className="flex-1 overflow-y-auto p-6 space-y-6">{children}</main>
        </div>
        <StatusBar />
      </body>
    </html>
  );
}
