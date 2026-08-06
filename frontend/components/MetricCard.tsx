'use client';

import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: LucideIcon;
  badgeText?: string;
  badgeType?: 'success' | 'info' | 'warning';
}

export default function MetricCard({
  title,
  value,
  description,
  icon: Icon,
  badgeText,
  badgeType = 'info',
}: MetricCardProps) {
  const badgeStyles = {
    success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    info: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    warning: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  };

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl p-4 space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-slate-400">{title}</span>
        {Icon && <Icon className="w-4 h-4 text-slate-400" />}
      </div>

      <div className="flex items-baseline justify-between">
        <span className="text-2xl font-bold text-white tracking-tight">{value}</span>
        {badgeText && (
          <span
            className={`px-2 py-0.5 rounded-full text-[10px] font-medium border ${badgeStyles[badgeType]}`}
          >
            {badgeText}
          </span>
        )}
      </div>

      {description && <p className="text-[11px] text-slate-500">{description}</p>}
    </div>
  );
}
