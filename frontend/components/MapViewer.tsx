'use client';

import { useState } from 'react';
import { Layers, MapPin, Eye, SlidersHorizontal } from 'lucide-react';

interface MapViewerProps {
  location?: string;
}

export default function MapViewer({ location = 'Hyderabad, India' }: MapViewerProps) {
  const [activeLayer, setActiveLayer] = useState<'NDVI' | 'NDWI' | 'NDBI' | 'LST'>('NDVI');
  const [opacity, setOpacity] = useState<number>(0.85);

  const layerOptions: Array<'NDVI' | 'NDWI' | 'NDBI' | 'LST'> = ['NDVI', 'NDWI', 'NDBI', 'LST'];

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl overflow-hidden flex flex-col">
      {/* Map Header */}
      <div className="px-4 py-3 border-b border-slate-800 bg-[#0f172a] flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <MapPin className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-semibold text-white">Region of Interest: {location}</span>
        </div>

        <div className="flex items-center space-x-2">
          {layerOptions.map((lyr) => (
            <button
              key={lyr}
              onClick={() => setActiveLayer(lyr)}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                activeLayer === lyr
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {lyr}
            </button>
          ))}
        </div>
      </div>

      {/* Map Canvas Simulated Box */}
      <div className="relative h-64 bg-slate-950 flex items-center justify-center overflow-hidden border-b border-slate-800">
        <div
          className="absolute inset-0 opacity-40 bg-[radial-gradient(#3b82f6_1px,transparent_1px)] [background-size:16px_16px]"
          style={{ opacity }}
        />

        <div className="relative z-10 text-center space-y-2 p-6 bg-slate-900/80 backdrop-blur rounded-xl border border-slate-800 max-w-sm">
          <div className="flex justify-center">
            <Layers className="w-8 h-8 text-blue-400 animate-pulse" />
          </div>
          <h4 className="text-xs font-semibold text-white">Google Earth Engine Raster Preview</h4>
          <p className="text-[11px] text-slate-400">
            Active Layer: <span className="text-blue-400 font-semibold">{activeLayer} Index</span>
          </p>
          <p className="text-[10px] text-slate-500">COPERNICUS/S2_SR_HARMONIZED (10m Resolution)</p>
        </div>

        {/* Legend Overlay */}
        <div className="absolute bottom-3 left-3 bg-slate-900/90 border border-slate-800 p-2 rounded text-[10px] text-slate-300 space-y-1">
          <span className="font-semibold text-white">Palette</span>
          <div className="flex items-center space-x-1">
            <span className="w-3 h-3 rounded-full bg-blue-900"></span>
            <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
            <span className="w-3 h-3 rounded-full bg-amber-400"></span>
            <span className="w-3 h-3 rounded-full bg-red-600"></span>
          </div>
        </div>
      </div>

      {/* Controls Footer */}
      <div className="px-4 py-2.5 bg-[#0f172a] flex items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center space-x-2">
          <SlidersHorizontal className="w-3.5 h-3.5 text-slate-500" />
          <span>Layer Opacity:</span>
          <input
            type="range"
            min="0.1"
            max="1.0"
            step="0.05"
            value={opacity}
            onChange={(e) => setOpacity(parseFloat(e.target.value))}
            className="w-24 accent-blue-500"
          />
          <span className="font-mono text-white">{Math.round(opacity * 100)}%</span>
        </div>
        <span className="text-[10px] text-slate-500">ROI Bounding Box: [78.47, 17.38, 78.52, 17.44]</span>
      </div>
    </div>
  );
}
