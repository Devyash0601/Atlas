'use client';

import MapContainer from './map/MapContainer';

interface MapViewerProps {
  location?: string;
  startDate?: string;
  endDate?: string;
  cloudThreshold?: number;
}

export default function MapViewer({
  location = 'Hyderabad, India',
  startDate = '2016-01-01',
  endDate = '2025-12-31',
  cloudThreshold = 20.0,
}: MapViewerProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between px-1">
        <div>
          <h2 className="text-sm font-semibold text-white tracking-tight">
            Interactive Earth Observation GIS Map Canvas
          </h2>
          <p className="text-xs text-slate-400">
            Study Region: <span className="text-blue-400 font-medium">{location}</span> • Date Range: <span className="text-emerald-400 font-mono">{startDate} to {endDate}</span> • Max Cloud: <span className="text-sky-400 font-mono">{cloudThreshold}%</span>
          </p>
        </div>
        <span className="text-[10px] text-emerald-400 font-mono px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
          Leaflet GIS Engine • Live GEE Tiles
        </span>
      </div>

      <MapContainer
        location={location}
        startDate={startDate}
        endDate={endDate}
        cloudThreshold={cloudThreshold}
      />
    </div>
  );
}
