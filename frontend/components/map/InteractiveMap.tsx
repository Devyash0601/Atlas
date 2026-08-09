'use client';

import React, { useEffect } from 'react';
import {
  MapContainer as LeafletMapContainer,
  TileLayer,
  GeoJSON,
  ScaleControl,
  useMapEvents,
  useMap,
} from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useMapContext } from './MapContext';
import CoordinateDisplay from './CoordinateDisplay';
import LayerSwitcher from './LayerSwitcher';
import OpacitySlider from './OpacitySlider';
import Legend from './Legend';
import { AlertCircle, Loader2, RefreshCw } from 'lucide-react';

// Fix Leaflet marker icon asset paths in Next.js
// @ts-ignore
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

function MapEventListener() {
  const { setCursorCoords, setCurrentZoom } = useMapContext();

  useMapEvents({
    mousemove(e) {
      setCursorCoords({ lat: e.latlng.lat, lng: e.latlng.lng });
    },
    mouseout() {
      setCursorCoords(null);
    },
    zoomend(e) {
      setCurrentZoom(e.target.getZoom());
    },
  });

  return null;
}

function MapViewController({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom, { animate: true });
  }, [center, zoom, map]);

  return null;
}

export default function InteractiveMap() {
  const { state, refetchTiles } = useMapContext();

  const roiStyle = {
    color: '#3b82f6', // Blue border
    weight: 2,
    fillColor: '#3b82f6',
    fillOpacity: state.opacity * 0.3,
  };

  const isLst = state.selectedLayer === 'lst' || state.selectedLayer === 'LST';
  const isNdbi = state.selectedLayer === 'ndbi' || state.selectedLayer === 'NDBI';
  const isNdwi = state.selectedLayer === 'ndwi' || state.selectedLayer === 'NDWI';
  const isNdvi = state.selectedLayer === 'ndvi' || state.selectedLayer === 'NDVI';
  const isNdbiChange = state.selectedLayer === 'ndbi_change' || state.selectedLayer === 'NDBI Change';
  const isLstChange = state.selectedLayer === 'lst_change' || state.selectedLayer === 'LST Change';

  const isGeeTileActive =
    state.selectedLayer === 'sentinel_rgb' ||
    state.selectedLayer === 'Satellite' ||
    isNdvi ||
    isNdwi ||
    isNdbi ||
    isLst ||
    isNdbiChange ||
    isLstChange;

  const layerLoadingTitle = isLstChange
    ? 'Landsat ΔLST Change (°C)'
    : isNdbiChange
    ? 'Sentinel-2 ΔNDBI Change'
    : isLst
    ? 'Landsat LST (°C)'
    : isNdbi
    ? 'Sentinel-2 NDBI'
    : isNdwi
    ? 'Sentinel-2 NDWI'
    : isNdvi
    ? 'Sentinel-2 NDVI'
    : 'Sentinel-2 RGB';

  return (
    <div className="relative w-full h-[430px] rounded-xl overflow-hidden border border-slate-800 bg-[#090d16] shadow-xl">
      <LeafletMapContainer
        center={state.center}
        zoom={state.zoom}
        scrollWheelZoom={true}
        doubleClickZoom={true}
        zoomControl={true}
        dragging={true}
        className="w-full h-full z-0"
      >
        <MapViewController center={state.center} zoom={state.zoom} />
        <MapEventListener />

        {/* Base OpenStreetMap TileLayer */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* GEE Satellite TileLayer (RGB, NDVI, NDWI, NDBI, LST, ΔNDBI, ΔLST) */}
        {isGeeTileActive && state.tileUrl && (
          <TileLayer
            key={state.tileUrl}
            url={state.tileUrl}
            opacity={state.opacity}
            attribution={
              isLst || isLstChange
                ? 'Google Earth Engine • USGS Landsat Collection 2 Level-2'
                : 'Google Earth Engine • Copernicus Sentinel-2'
            }
          />
        )}

        {/* ROI GeoJSON Polygon Overlay */}
        {state.roiGeoJson && (
          <GeoJSON key={JSON.stringify(state.center)} data={state.roiGeoJson} style={roiStyle} />
        )}

        <ScaleControl position="bottomleft" metric={true} imperial={false} />
      </LeafletMapContainer>

      {/* Loading Overlay */}
      {state.isTileLoading && (
        <div className="absolute inset-0 z-20 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center pointer-events-none">
          <div className="bg-[#0f172a] border border-amber-500/30 rounded-xl p-4 shadow-2xl flex items-center space-x-3 text-xs text-white">
            <Loader2 className="w-5 h-5 text-amber-400 animate-spin" />
            <div className="space-y-0.5">
              <p className="font-semibold text-amber-400">
                Fetching {layerLoadingTitle} Map Tiles...
              </p>
              <p className="text-[10px] text-slate-400">
                {isLst || isLstChange ? 'Google Earth Engine • LANDSAT/LC08/C02/T1_L2' : 'Google Earth Engine • COPERNICUS/S2_SR_HARMONIZED'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error Alert Banner */}
      {state.errorMessage && (
        <div className="absolute top-3 left-3 right-64 z-20 bg-red-950/90 border border-red-500/40 rounded-lg p-2.5 flex items-center justify-between text-xs text-red-300 shadow-xl">
          <div className="flex items-center space-x-2 truncate">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
            <span className="truncate">{state.errorMessage}</span>
          </div>
          <button
            onClick={refetchTiles}
            className="ml-2 px-2 py-1 bg-red-900/60 hover:bg-red-800 text-white rounded text-[10px] font-semibold flex items-center space-x-1 transition-colors flex-shrink-0"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Retry</span>
          </button>
        </div>
      )}

      {/* Floating Map Overlays */}

      {/* Top Right: Layer Switcher */}
      <div className="absolute top-3 right-3 z-10">
        <LayerSwitcher />
      </div>

      {/* Bottom Left: Coordinates Display */}
      <div className="absolute bottom-3 left-24 z-10">
        <CoordinateDisplay />
      </div>

      {/* Bottom Center: Opacity Slider */}
      <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-10">
        <OpacitySlider />
      </div>

      {/* Bottom Right: Legend */}
      <div className="absolute bottom-3 right-3 z-10">
        <Legend />
      </div>
    </div>
  );
}
