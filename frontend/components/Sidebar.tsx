'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Search,
  FolderGit2,
  BookOpen,
  FileText,
  BarChart3,
  Settings as SettingsIcon,
  Info,
  Layers,
} from 'lucide-react';

export default function Sidebar() {
  const pathname = usePathname();

  const menuItems = [
    { label: 'Research Workspace', href: '/research', icon: Search },
    { label: 'Project Explorer', href: '/projects', icon: FolderGit2 },
    { label: 'Literature Browser', href: '/literature', icon: BookOpen },
    { label: 'Report Viewer', href: '/reports', icon: FileText },
    { label: 'Metrics Dashboard', href: '/metrics', icon: BarChart3 },
    { label: 'Settings', href: '/settings', icon: SettingsIcon },
    { label: 'About & Docs', href: '/about', icon: Info },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-[#0f172a]/60 p-4 space-y-6 flex flex-col justify-between hidden lg:flex">
      <div className="space-y-4">
        <div className="px-3 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-2">
          <Layers className="w-3.5 h-3.5 text-blue-400" />
          <span>Navigation</span>
        </div>

        <nav className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600/15 text-blue-400 border border-blue-500/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg space-y-1">
        <p className="text-[11px] font-semibold text-slate-300">Google Earth Engine</p>
        <p className="text-[10px] text-slate-500">Sentinel-2 / Landsat Active</p>
      </div>
    </aside>
  );
}
