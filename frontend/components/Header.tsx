'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Activity, Layers, Terminal } from 'lucide-react';

export default function Header() {
  const pathname = usePathname();

  const navLinks = [
    { label: 'Research', href: '/research' },
    { label: 'Projects', href: '/projects' },
    { label: 'Literature', href: '/literature' },
    { label: 'Reports', href: '/reports' },
    { label: 'Metrics', href: '/metrics' },
    { label: 'Settings', href: '/settings' },
    { label: 'About', href: '/about' },
  ];

  return (
    <header className="border-b border-slate-800 bg-[#0f172a]/95 backdrop-blur sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between">
      <div className="flex items-center space-x-6">
        <Link href="/" className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white shadow-md shadow-blue-500/20 text-sm">
            A
          </div>
          <div>
            <h1 className="font-semibold text-base text-white leading-tight">ATLAS-EO</h1>
            <p className="text-[10px] text-slate-400">Autonomous Science Platform</p>
          </div>
        </Link>

        <nav className="hidden md:flex items-center space-x-1 pl-4 border-l border-slate-800">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="flex items-center space-x-3">
        <span className="hidden sm:inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <Activity className="w-3 h-3 mr-1.5" />
          Backend API Online
        </span>
        <span className="inline-flex items-center px-2.5 py-1 rounded-md text-[11px] font-mono bg-slate-800 text-slate-300 border border-slate-700">
          <Terminal className="w-3 h-3 mr-1 text-blue-400" />
          v0.5.0-core
        </span>
      </div>
    </header>
  );
}
