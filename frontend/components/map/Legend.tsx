'use client';

import { useMapContext } from './MapContext';

export default function Legend() {
  const { state } = useMapContext();
  const meta = state.metadata;

  const isNdviActive = state.selectedLayer === 'ndvi' || state.selectedLayer === 'NDVI';
  const isNdwiActive = state.selectedLayer === 'ndwi' || state.selectedLayer === 'NDWI';
  const isNdbiActive = state.selectedLayer === 'ndbi' || state.selectedLayer === 'NDBI';
  const isLstActive = state.selectedLayer === 'lst' || state.selectedLayer === 'LST';
  const isNdbiChangeActive = state.selectedLayer === 'ndbi_change' || state.selectedLayer === 'NDBI Change';
  const isLstChangeActive = state.selectedLayer === 'lst_change' || state.selectedLayer === 'LST Change';
  const isSentinelActive =
    state.selectedLayer === 'sentinel_rgb' || state.selectedLayer === 'Satellite';

  return (
    <div className="bg-[#0f172a]/95 backdrop-blur border border-slate-800 rounded-lg p-2.5 space-y-2 shadow-lg text-[10px] text-slate-300 min-w-[220px]">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1 font-semibold text-white">
        <span>Map Legend</span>
        <span className="text-amber-400 font-mono">
          {isLstChangeActive
            ? 'LST Change (°C)'
            : isNdbiChangeActive
            ? 'ΔNDBI Change'
            : isLstActive
            ? 'LST Thermal (°C)'
            : isNdbiActive
            ? 'NDBI Index'
            : isNdwiActive
            ? 'NDWI Index'
            : isNdviActive
            ? 'NDVI Index'
            : isSentinelActive
            ? 'Sentinel-2 RGB'
            : 'OpenStreetMap'}
        </span>
      </div>

      <div className="space-y-1">
        <div className="flex justify-between text-slate-400">
          <span>Active Layer:</span>
          <span className="text-slate-200 font-medium truncate max-w-[120px]">
            {isLstChangeActive
              ? 'LST Change (2016–2025)'
              : isNdbiChangeActive
              ? 'NDBI Change (2016–2025)'
              : isLstActive
              ? 'Surface Temp (LST)'
              : isNdbiActive
              ? 'Built-up Index (NDBI)'
              : isNdwiActive
              ? 'Water Index (NDWI)'
              : isNdviActive
              ? 'Vegetation (NDVI)'
              : isSentinelActive
              ? 'Sentinel True Color'
              : 'OpenStreetMap'}
          </span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>Dataset:</span>
          <span className="text-slate-200 font-mono truncate max-w-[110px]">
            {meta?.dataset || (isLstActive || isLstChangeActive ? 'LC08/C02/T1_L2' : 'S2_SR_HARMONIZED')}
          </span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>Opacity:</span>
          <span className="text-slate-200 font-mono">{Math.round(state.opacity * 100)}%</span>
        </div>
      </div>

      {isLstChangeActive ? (
        <div className="pt-1 border-t border-slate-800 space-y-1">
          <div className="flex justify-between text-[9px] text-slate-400 font-mono">
            <span>Formula:</span>
            <span className="text-amber-400 font-semibold">LST_2025 − LST_2016 (°C)</span>
          </div>
          {/* Diverging LST Change Gradient: blue (cooling) -> white (no change) -> red (warming) */}
          <div className="h-2.5 w-full rounded bg-gradient-to-r from-[#2166ac] via-[#67a9cf] via-[#f7f7f7] via-[#ef8a62] to-[#b2182b] border border-slate-700" />
          <div className="flex justify-between text-[9px] text-slate-400 font-mono">
            <span>-10°C (Cooling)</span>
            <span>0°C</span>
            <span>+10°C (Warming)</span>
          </div>
        </div>
      ) : isNdbiChangeActive ? (
        <div className="pt-1 border-t border-slate-800 space-y-1">
          <div className="flex justify-between text-[9px] text-slate-400 font-mono">
            <span>Formula:</span>
            <span className="text-amber-400 font-semibold">NDBI_2025 − NDBI_2016</span>
          </div>
          {/* Diverging NDBI Change Gradient: blue (NDBI ↓) -> white (no change) -> red (NDBI ↑) */}
          <div className="h-2.5 w-full rounded bg-gradient-to-r from-[#2166ac] via-[#67a9cf] via-[#f7f7f7] via-[#ef8a62] to-[#b2182b] border border-slate-700" />
          <div className="flex justify-between text-[9px] text-slate-400 font-mono">
            <span>-1.0 (NDBI ↓)</span>
            <span>0.0</span>
            <span>+1.0 (NDBI ↑)</span>
          </div>
        </div>
      ) : isLstActive ? (
        <div className="pt-1 border-t border-slate-800 space-y-1">
          <div className="flex justify-between text-[9px] text-slate-400 font-mono">
            <span>Formula:</span>
            <span className="text-red-400 font-semibold">ST_B10 * 0.0034 + 149 - 273 (°C)</span>
          </div>
          {/* LST Thermal Palette Gradient: cool blue -> light cyan -> soft yellow -> orange -> dark red */}
          <div className="h-2.5 w-full rounded bg-gradient-to-r from-[#313695] via-[#4575b4] via-[#74add1] via-[#ffffbf] via-[#fdae61] via-[#f46d43] to-[#a50026] border border-slate-700" />
          <div className="flex justify-between text-[9px] text-slate-400 font-mono">
            <span>15°C (Cool)</span>
            <span>32.5°C</span>
            <span>50°C (Hot)</span>
          </div>
        </div>
      ) : isNdbiActive ? (
        <div className="pt-1 border-t border-slate-800 space-y-1">
          <div className="flex justify-between text-[9px] text-slate-400 font-mono">
            <span>Formula:</span>
            <span className="text-orange-400 font-semibold">(B11 - B8)/(B11 + B8)</span>
          </div>
          {/* NDBI Built-up Palette Gradient: blue/cyan (water/veg) -> yellow -> orange/red (urban) */}
          <div className="h-2.5 w-full rounded bg-gradient-to-r from-[#313695] via-[#74add1] via-[#abd9e9] via-[#ffffbf] via-[#fdae61] via-[#f46d43] to-[#a50026] border border-slate-700" />
          <div className="flex justify-between text-[9px] text-slate-400 font-mono">
            <span>-1.0 (Non-Built)</span>
            <span>0.0</span>
            <span>+1.0 (Built-up)</span>
          </div>
        </div>
      ) : isNdwiActive ? (
        <div className="pt-1 border-t border-slate-800 space-y-1">
          <div className="flex justify-between text-[9px] text-slate-400 font-mono">
            <span>Formula:</span>
            <span className="text-cyan-400 font-semibold">(B3 - B8)/(B3 + B8)</span>
          </div>
          {/* NDWI Water Palette Gradient: brown -> light yellow -> light teal -> cyan -> bright blue -> deep navy blue */}
          <div className="h-2.5 w-full rounded bg-gradient-to-r from-[#8c510a] via-[#d8b365] via-[#f6e8c3] via-[#c7eae5] via-[#3388ff] to-[#000080] border border-slate-700" />
          <div className="flex justify-between text-[9px] text-slate-400 font-mono">
            <span>-1.0 (Dry Land)</span>
            <span>0.0</span>
            <span>+1.0 (Water)</span>
          </div>
        </div>
      ) : isNdviActive ? (
        <div className="pt-1 border-t border-slate-800 space-y-1">
          <div className="flex justify-between text-[9px] text-slate-400 font-mono">
            <span>Formula:</span>
            <span className="text-emerald-400 font-semibold">(B8 - B4)/(B8 + B4)</span>
          </div>
          {/* NDVI Palette Gradient: brown -> light yellow -> teal -> dark teal green */}
          <div className="h-2.5 w-full rounded bg-gradient-to-r from-[#8c510a] via-[#d8b365] via-[#f6e8c3] via-[#c7eae5] via-[#5ab4ac] to-[#01665e] border border-slate-700" />
          <div className="flex justify-between text-[9px] text-slate-400 font-mono">
            <span>-1.0 (Non-Veg)</span>
            <span>0.0</span>
            <span>+1.0 (Dense)</span>
          </div>
        </div>
      ) : (
        <div className="pt-1 border-t border-slate-800 space-y-1">
          <span className="text-[9px] text-slate-500 uppercase tracking-wider font-semibold">
            {isSentinelActive ? 'RGB Band Composite (B4/B3/B2)' : 'Basemap Color Scheme'}
          </span>
          <div className="h-2 w-full rounded bg-gradient-to-r from-blue-900 via-emerald-500 via-amber-400 to-red-600 border border-slate-700" />
          <div className="flex justify-between text-[9px] text-slate-500 font-mono">
            <span>0.0 Refl</span>
            <span>0.3 Refl</span>
          </div>
        </div>
      )}
    </div>
  );
}
