'use client';

import { Cpu, HardDrive, ShieldCheck, Zap } from 'lucide-react';

export default function StatusBar() {
  return (
    <footer className="border-t border-slate-800 bg-[#0f172a] px-6 py-2 flex items-center justify-between text-[11px] text-slate-400">
      <div className="flex items-center space-x-6">
        <span className="flex items-center space-x-1.5">
          <Cpu className="w-3.5 h-3.5 text-blue-400" />
          <span>Ollama: qwen2.5-coder:14b</span>
        </span>
        <span className="flex items-center space-x-1.5">
          <HardDrive className="w-3.5 h-3.5 text-indigo-400" />
          <span>VRAM: ~11.0 GB Max (M3 Pro)</span>
        </span>
        <span className="flex items-center space-x-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Zero Paid APIs</span>
        </span>
      </div>

      <div className="flex items-center space-x-4">
        <span className="flex items-center space-x-1 text-slate-500">
          <Zap className="w-3 h-3 text-amber-400" />
          <span>Execution Protocol: Declarative GEE</span>
        </span>
      </div>
    </footer>
  );
}
