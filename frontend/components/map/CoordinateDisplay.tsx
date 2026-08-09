'use client';

import { useMapContext } from './MapContext';

export default function CoordinateDisplay() {
  const { state } = useMapContext();
  const lat = state.cursorCoords ? state.cursorCoords.lat.toFixed(4) : state.center[0].toFixed(4);
  const lng = state.cursorCoords ? state.cursorCoords.lng.toFixed(4) : state.center[1].toFixed(4);

  return (
    <div className="bg-[#0f172a]/90 backdrop-blur border border-slate-800 rounded px-2.5 py-1 text-[10px] font-mono text-slate-300 flex items-center space-x-3 shadow-md">
      <div>
        <span className="text-slate-500">Lat:</span>{' '}
        <span className="text-blue-400 font-semibold">{lat}°</span>
      </div>
      <div>
        <span className="text-slate-500">Lng:</span>{' '}
        <span className="text-blue-400 font-semibold">{lng}°</span>
      </div>
      <div>
        <span className="text-slate-500">Zoom:</span>{' '}
        <span className="text-emerald-400 font-semibold">{state.currentZoom}</span>
      </div>
    </div>
  );
}
