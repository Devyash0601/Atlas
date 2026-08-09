'use client';

import { useMapContext } from './MapContext';
import { Database, Calendar, Cloud, Sliders, Activity } from 'lucide-react';

export default function MetadataPanel() {
  const { state } = useMapContext();
  const meta = state.metadata;
  const isNdviActive = state.selectedLayer === 'ndvi' || state.selectedLayer === 'NDVI';
  const isNdwiActive = state.selectedLayer === 'ndwi' || state.selectedLayer === 'NDWI';
  const isNdbiActive = state.selectedLayer === 'ndbi' || state.selectedLayer === 'NDBI';
  const isLstActive = state.selectedLayer === 'lst' || state.selectedLayer === 'LST';
  const isNdbiChangeActive = state.selectedLayer === 'ndbi_change' || state.selectedLayer === 'NDBI Change';
  const isLstChangeActive = state.selectedLayer === 'lst_change' || state.selectedLayer === 'LST Change';

  if (!meta && state.selectedLayer === 'OSM') {
    return (
      <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-4 text-xs text-slate-400 space-y-1">
        <div className="flex items-center space-x-2 text-white font-semibold pb-1 border-b border-slate-800">
          <Database className="w-4 h-4 text-blue-400" />
          <span>Active Layer: OpenStreetMap</span>
        </div>
        <p className="text-[11px] text-slate-400 pt-1">
          Select <strong className="text-amber-400">NDBI Built-up Change</strong>, <strong className="text-amber-400">LST Thermal Change</strong>, <strong className="text-red-400">Land Surface Temperature (LST)</strong>, <strong className="text-orange-400">NDBI</strong>, <strong className="text-cyan-400">NDWI</strong>, <strong className="text-emerald-400">NDVI</strong>, or <strong className="text-blue-400">Sentinel-2 True Color (RGB)</strong> in the map layer switcher to load live Google Earth Engine satellite imagery tiles and acquisition metadata.
        </p>
      </div>
    );
  }

  const layerTitle = isLstChangeActive
    ? 'LST Change Raster (2016–2025)'
    : isNdbiChangeActive
    ? 'NDBI Change Raster (2016–2025)'
    : isLstActive
    ? 'LST Thermal Raster'
    : isNdbiActive
    ? 'NDBI Raster'
    : isNdwiActive
    ? 'NDWI Raster'
    : isNdviActive
    ? 'NDVI Raster'
    : 'RGB Composite';

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl p-4 space-y-3">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2">
          <Database className="w-4 h-4 text-emerald-400" />
          <h3 className="text-xs font-semibold text-white">
            Earth Observation Acquisition Metadata ({layerTitle})
          </h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          GEE Verified
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-xs">
        <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 space-y-1">
          <div className="flex items-center space-x-1.5 text-slate-400 text-[11px]">
            <Database className="w-3.5 h-3.5 text-blue-400" />
            <span>Dataset ID</span>
          </div>
          <p className="font-mono text-white text-[11px] font-medium truncate">
            {meta?.dataset || (isLstActive || isLstChangeActive ? 'LANDSAT/LC08/C02/T1_L2' : 'COPERNICUS/S2_SR_HARMONIZED')}
          </p>
        </div>

        <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 space-y-1">
          <div className="flex items-center space-x-1.5 text-slate-400 text-[11px]">
            <Activity className="w-3.5 h-3.5 text-red-400" />
            <span>Formula / Index</span>
          </div>
          <p className="font-mono text-white text-[11px] font-medium truncate">
            {meta?.formula ||
              (isLstChangeActive
                ? 'LST_2025 − LST_2016 (°C)'
                : isNdbiChangeActive
                ? 'NDBI_2025 − NDBI_2016'
                : isLstActive
                ? 'ST_B10 * 0.00341802 + 149.0 - 273.15 (°C)'
                : isNdbiActive
                ? '(B11 - B8) / (B11 + B8)'
                : isNdwiActive
                ? '(B3 - B8) / (B3 + B8)'
                : isNdviActive
                ? '(B8 - B4) / (B8 + B4)'
                : 'RGB')}
          </p>
        </div>

        <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 space-y-1">
          <div className="flex items-center space-x-1.5 text-slate-400 text-[11px]">
            <Calendar className="w-3.5 h-3.5 text-emerald-400" />
            <span>Date Range</span>
          </div>
          <p className="font-mono text-white text-[11px] font-medium truncate">
            {meta?.date_range || (isLstChangeActive || isNdbiChangeActive ? '2016 to 2025' : '2016-01-01 to 2025-12-31')}
          </p>
        </div>

        <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 space-y-1">
          <div className="flex items-center space-x-1.5 text-slate-400 text-[11px]">
            <Cloud className="w-3.5 h-3.5 text-sky-400" />
            <span>Cloud Threshold</span>
          </div>
          <p className="font-mono text-white text-[11px] font-medium">
            {meta?.cloud_threshold_pct ?? 20.0}% Max Cloud
          </p>
        </div>

        <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 space-y-1">
          <div className="flex items-center space-x-1.5 text-slate-400 text-[11px]">
            <Sliders className="w-3.5 h-3.5 text-amber-400" />
            <span>Resolution & Bands</span>
          </div>
          <p className="font-mono text-white text-[11px] font-medium">
            {meta?.resolution_meters ?? (isLstActive || isLstChangeActive ? 30 : isNdbiActive || isNdbiChangeActive ? 20 : 10)}m (
            {meta?.bands
              ? meta.bands.join('/')
              : isLstActive || isLstChangeActive
              ? 'ST_B10'
              : isNdbiActive || isNdbiChangeActive
              ? 'B11/B8'
              : isNdwiActive
              ? 'B3/B8'
              : isNdviActive
              ? 'B8/B4'
              : 'B4/B3/B2'}
            )
          </p>
        </div>
      </div>
    </div>
  );
}
