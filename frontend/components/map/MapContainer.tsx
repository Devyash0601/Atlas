'use client';

import dynamic from 'next/dynamic';
import { MapProvider } from './MapContext';
import MetadataPanel from './MetadataPanel';

const DynamicInteractiveMap = dynamic(() => import('./InteractiveMap'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[400px] rounded-xl border border-slate-800 bg-[#090d16] flex items-center justify-center text-xs text-slate-400 font-mono">
      <div className="flex items-center space-x-2">
        <span className="w-3 h-3 rounded-full bg-blue-500 animate-ping" />
        <span>Initializing Production Leaflet GIS Engine...</span>
      </div>
    </div>
  ),
});

export interface MapContainerProps {
  location?: string;
  startDate?: string;
  endDate?: string;
  cloudThreshold?: number;
}

export default function MapContainer({
  location = 'Hyderabad',
  startDate = '2016-01-01',
  endDate = '2025-12-31',
  cloudThreshold = 20.0,
}: MapContainerProps) {
  return (
    <MapProvider
      initialLocation={location}
      initialStartDate={startDate}
      initialEndDate={endDate}
      initialCloudThreshold={cloudThreshold}
    >
      <div className="space-y-4">
        <DynamicInteractiveMap />
        <MetadataPanel />
      </div>
    </MapProvider>
  );
}
