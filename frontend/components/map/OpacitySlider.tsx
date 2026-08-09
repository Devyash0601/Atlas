'use client';

import { useMapContext } from './MapContext';
import { SlidersHorizontal } from 'lucide-react';

export default function OpacitySlider() {
  const { state, setOpacity } = useMapContext();

  return (
    <div className="bg-[#0f172a]/90 backdrop-blur border border-slate-800 rounded-lg px-3 py-1.5 flex items-center space-x-2 text-[11px] text-slate-300 shadow-md">
      <SlidersHorizontal className="w-3.5 h-3.5 text-blue-400" />
      <span className="font-medium text-slate-400">Layer Opacity:</span>
      <input
        type="range"
        min="0"
        max="1"
        step="0.05"
        value={state.opacity}
        onChange={(e) => setOpacity(parseFloat(e.target.value))}
        className="w-24 accent-blue-500 cursor-pointer"
      />
      <span className="font-mono text-white min-w-[32px]">
        {Math.round(state.opacity * 100)}%
      </span>
    </div>
  );
}
