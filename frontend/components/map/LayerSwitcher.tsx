'use client';

import { useMapContext } from './MapContext';
import { Layers, Loader2 } from 'lucide-react';

export default function LayerSwitcher() {
  const { state, setSelectedLayer } = useMapContext();

  const baseLayerOptions = [
    { id: 'OSM', name: 'OpenStreetMap', isActive: true },
    { id: 'sentinel_rgb', name: 'Sentinel-2 True Color (RGB)', isActive: true },
    { id: 'ndvi', name: 'Normalized Difference Vegetation Index (NDVI)', isActive: true },
    { id: 'ndwi', name: 'Normalized Difference Water Index (NDWI)', isActive: true },
    { id: 'ndbi', name: 'Normalized Difference Built-up Index (NDBI)', isActive: true },
    { id: 'lst', name: 'Land Surface Temperature (LST)', isActive: true },
  ];

  const changeLayerOptions = [
    { id: 'ndbi_change', name: 'NDBI Built-up Change (2016–2025)', isActive: true },
    { id: 'lst_change', name: 'LST Thermal Change (2016–2025)', isActive: true },
  ];

  const isOptionSelected = (id: string) => {
    return (
      state.selectedLayer === id ||
      (state.selectedLayer === 'Satellite' && id === 'sentinel_rgb') ||
      (state.selectedLayer === 'NDVI' && id === 'ndvi') ||
      (state.selectedLayer === 'NDWI' && id === 'ndwi') ||
      (state.selectedLayer === 'NDBI' && id === 'ndbi') ||
      (state.selectedLayer === 'LST' && id === 'lst') ||
      (state.selectedLayer === 'NDBI Change' && id === 'ndbi_change') ||
      (state.selectedLayer === 'LST Change' && id === 'lst_change')
    );
  };

  return (
    <div className="bg-[#0f172a]/95 backdrop-blur border border-slate-800 rounded-lg p-2.5 space-y-2.5 shadow-lg min-w-[250px]">
      <div className="flex items-center space-x-1.5 text-[11px] font-semibold text-white pb-1.5 border-b border-slate-800">
        <Layers className="w-3.5 h-3.5 text-blue-400" />
        <span>Map Layer Selector</span>
      </div>

      <div className="space-y-1">
        <div className="text-[9px] font-semibold tracking-wider text-slate-400 uppercase px-1 pb-0.5">
          Base Satellite Layers
        </div>
        {baseLayerOptions.map((lyr) => {
          const isSelected = isOptionSelected(lyr.id);

          return (
            <button
              key={lyr.id}
              onClick={() => {
                if (lyr.isActive) {
                  setSelectedLayer(lyr.id);
                }
              }}
              disabled={!lyr.isActive}
              className={`w-full text-left px-2 py-1.5 rounded text-[10px] font-medium flex items-center justify-between transition-colors ${
                isSelected
                  ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30'
                  : lyr.isActive
                  ? 'text-slate-300 hover:text-white hover:bg-slate-800/60 cursor-pointer'
                  : 'text-slate-600 cursor-not-allowed opacity-60'
              }`}
            >
              <span className="truncate pr-2">{lyr.name}</span>
              {isSelected && state.isTileLoading ? (
                <Loader2 className="w-3 h-3 text-emerald-400 animate-spin flex-shrink-0" />
              ) : isSelected ? (
                <span className="text-[9px] px-1 py-0.2 rounded bg-emerald-500/20 text-emerald-400 font-semibold flex-shrink-0">
                  Active
                </span>
              ) : (
                <span className="text-[9px] px-1 py-0.2 rounded bg-slate-800 text-slate-400 flex-shrink-0">
                  GEE Live
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="space-y-1 pt-1 border-t border-slate-800">
        <div className="text-[9px] font-semibold tracking-wider text-amber-400 uppercase px-1 pb-0.5 flex items-center justify-between">
          <span>Spatial Change Products</span>
          <span className="text-[8px] text-amber-400/80 font-normal">GEE ΔRaster</span>
        </div>
        {changeLayerOptions.map((lyr) => {
          const isSelected = isOptionSelected(lyr.id);

          return (
            <button
              key={lyr.id}
              onClick={() => {
                if (lyr.isActive) {
                  setSelectedLayer(lyr.id);
                }
              }}
              disabled={!lyr.isActive}
              className={`w-full text-left px-2 py-1.5 rounded text-[10px] font-medium flex items-center justify-between transition-colors ${
                isSelected
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/60 cursor-pointer'
              }`}
            >
              <span className="truncate pr-2">{lyr.name}</span>
              {isSelected && state.isTileLoading ? (
                <Loader2 className="w-3 h-3 text-amber-400 animate-spin flex-shrink-0" />
              ) : isSelected ? (
                <span className="text-[9px] px-1 py-0.2 rounded bg-amber-500/20 text-amber-300 font-semibold flex-shrink-0">
                  Active
                </span>
              ) : (
                <span className="text-[9px] px-1 py-0.2 rounded bg-amber-950/40 text-amber-400 border border-amber-500/20 flex-shrink-0">
                  Analysis
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
