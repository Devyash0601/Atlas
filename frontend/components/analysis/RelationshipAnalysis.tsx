'use client';

import React, { useEffect, useState } from 'react';
import { apiClient, RelationshipAnalysisResponse } from '@/lib/api';
import ScatterPlot from './ScatterPlot';
import {
  Activity,
  AlertTriangle,
  BarChart3,
  BookOpen,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Database,
  Grid,
  Info,
  Layers,
  Loader2,
  RefreshCw,
  ShieldAlert,
  Sparkles,
  TrendingUp,
} from 'lucide-react';

interface RelationshipAnalysisProps {
  location?: string;
  startYear?: number;
  endYear?: number;
  cloudThreshold?: number;
}

export default function RelationshipAnalysis({
  location = 'Hyderabad',
  startYear = 2016,
  endYear = 2025,
  cloudThreshold = 20.0,
}: RelationshipAnalysisProps) {
  const [data, setData] = useState<RelationshipAnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showMethodology, setShowMethodology] = useState<boolean>(false);

  const fetchAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.getRelationshipAnalysis({
        location,
        start_year: startYear,
        end_year: endYear,
        cloud: cloudThreshold,
        sample_size: 5000,
        seed: 42,
      });
      setData(res);
    } catch (err: any) {
      setError(
        err?.message ||
          'Unable to calculate relationship analysis. Please check the research parameters and try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalysis();
  }, [location, startYear, endYear, cloudThreshold]);

  if (loading) {
    return (
      <div className="bg-[#0b101d] border border-slate-800 rounded-2xl p-8 shadow-xl flex flex-col items-center justify-center space-y-3 text-xs text-white my-6 min-h-[300px]">
        <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
        <div className="text-center space-y-1">
          <p className="font-semibold text-sm text-cyan-400">
            Running Earth Observation Analysis & Spatial Pairing...
          </p>
          <p className="text-xs text-slate-400">
            Calculating 30m projected metric grid pairing for {location} (2016 → 2025)
          </p>
          <p className="text-[11px] text-slate-500 font-mono">
            Sentinel-2 ΔNDBI (20m native) • Landsat ΔLST (30m native) • GEE Cloud Engine
          </p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-red-950/40 border border-red-500/30 rounded-2xl p-6 my-6 text-xs text-red-300 flex items-center justify-between shadow-xl">
        <div className="flex items-center space-x-3">
          <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <div>
            <p className="font-semibold text-sm text-red-200">Analysis Calculation Failed</p>
            <p className="text-xs text-red-300/80">
              {error || 'Unable to calculate relationship analysis. Please check parameters.'}
            </p>
          </div>
        </div>
        <button
          onClick={fetchAnalysis}
          className="px-3 py-1.5 bg-red-900/60 hover:bg-red-800 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-colors shadow-md"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry Analysis</span>
        </button>
      </div>
    );
  }

  const isPositive = data.correlation.pearson_r > 0;
  const isNegative = data.correlation.pearson_r < 0;

  return (
    <div className="bg-[#0b101d] border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-8 my-6">
      {/* 1. CHANGE ANALYSIS SECTION (2016 → 2025) */}
      <div className="space-y-3">
        <div className="flex items-center space-x-2 border-b border-slate-800/80 pb-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            {data.baseline_year} → {data.end_year} Change Analysis Summary
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* NDBI Change Card */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-cyan-400">NDBI Change (ΔNDBI)</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                Native 20m → Resampled 30m
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs pt-1">
              <div>
                <span className="text-[11px] text-slate-400 block">Baseline → Endpoint</span>
                <span className="font-mono text-slate-200">{data.baseline_year} → {data.end_year}</span>
              </div>
              <div>
                <span className="text-[11px] text-slate-400 block">Formula</span>
                <span className="font-mono text-slate-200">NDBI₂₀₂₅ − NDBI₂₀₁₆</span>
              </div>
              <div>
                <span className="text-[11px] text-slate-400 block">Study-area mean change</span>
                <span className="font-mono font-bold text-cyan-400">
                  {data.ndbi.mean_change >= 0 ? '+' : ''}
                  {data.ndbi.mean_change.toFixed(5)}
                </span>
              </div>
              <div>
                <span className="text-[11px] text-slate-400 block">Spatial StdDev</span>
                <span className="font-mono text-slate-300">{data.ndbi.std_change.toFixed(5)}</span>
              </div>
            </div>
          </div>

          {/* LST Change Card */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-amber-400">LST Change (ΔLST)</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                Native 30m (°C)
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs pt-1">
              <div>
                <span className="text-[11px] text-slate-400 block">Baseline → Endpoint</span>
                <span className="font-mono text-slate-200">{data.baseline_year} → {data.end_year}</span>
              </div>
              <div>
                <span className="text-[11px] text-slate-400 block">Formula</span>
                <span className="font-mono text-slate-200">LST₂₀₂₅ − LST₂₀₁₆</span>
              </div>
              <div>
                <span className="text-[11px] text-slate-400 block">Study-area mean change</span>
                <span className="font-mono font-bold text-amber-400">
                  {data.lst.mean_change >= 0 ? '+' : ''}
                  {data.lst.mean_change.toFixed(3)}°C
                </span>
              </div>
              <div>
                <span className="text-[11px] text-slate-400 block">Spatial StdDev</span>
                <span className="font-mono text-slate-300">{data.lst.std_change.toFixed(3)}°C</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. RELATIONSHIP ANALYSIS SECTION HEADER */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800/80 pb-4 gap-3">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-cyan-400" />
            <h3 className="text-sm font-bold text-white tracking-wide">
              Urban Expansion (ΔNDBI) ↔ Surface Temp Change (ΔLST) Spatial Relationship
            </h3>
          </div>
          <p className="text-xs text-slate-400">
            Spatial relationship between change in NDBI and change in land surface temperature ({data.baseline_year}–{data.end_year}) over {data.location}.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-[10px] font-mono">
          <span className="px-2.5 py-1 rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center space-x-1">
            <Grid className="w-3 h-3" />
            <span>Analysis Grid: {data.analysis_resolution_m}m ({data.metadata.analysis_crs})</span>
          </span>
          <span className="px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center space-x-1">
            <Database className="w-3 h-3" />
            <span>N = {data.sample_size.toLocaleString()} Paired Pixels</span>
          </span>
          <span className="px-2.5 py-1 rounded-md bg-purple-500/10 text-purple-400 border border-purple-500/20 flex items-center space-x-1">
            <CheckCircle2 className="w-3 h-3" />
            <span>Seed: {data.metadata.seed}</span>
          </span>
        </div>
      </div>

      {/* 3. KEY STATISTICS CARDS */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-3 text-xs">
        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 space-y-1">
          <div className="flex items-center space-x-1 text-slate-400 text-[11px]">
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            <span>Pearson r</span>
          </div>
          <p className="text-lg font-mono font-bold text-emerald-400">
            {data.correlation.pearson_r >= 0 ? '+' : ''}
            {data.correlation.pearson_r.toFixed(4)}
          </p>
          <p className="text-[10px] text-slate-400">Linear correlation</p>
        </div>

        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 space-y-1">
          <div className="flex items-center space-x-1 text-slate-400 text-[11px]">
            <BarChart3 className="w-3.5 h-3.5 text-cyan-400" />
            <span>Spearman ρ</span>
          </div>
          <p className="text-lg font-mono font-bold text-cyan-400">
            {data.correlation.spearman_rho >= 0 ? '+' : ''}
            {data.correlation.spearman_rho.toFixed(4)}
          </p>
          <p className="text-[10px] text-slate-400">Rank correlation</p>
        </div>

        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 space-y-1">
          <div className="flex items-center space-x-1 text-slate-400 text-[11px]">
            <TrendingUp className="w-3.5 h-3.5 text-amber-400" />
            <span>R² (Fit)</span>
          </div>
          <p className="text-lg font-mono font-bold text-amber-400">
            {data.regression.r_squared.toFixed(4)}
          </p>
          <p className="text-[10px] text-slate-400">Variance explained</p>
        </div>

        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 space-y-1">
          <div className="flex items-center space-x-1 text-slate-400 text-[11px]">
            <Activity className="w-3.5 h-3.5 text-red-400" />
            <span>OLS Slope (β₁)</span>
          </div>
          <p className="text-lg font-mono font-bold text-red-400">
            {data.regression.slope >= 0 ? '+' : ''}
            {data.regression.slope.toFixed(4)}
          </p>
          <p className="text-[10px] text-slate-400">°C / NDBI unit</p>
        </div>

        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 space-y-1">
          <div className="flex items-center space-x-1 text-slate-400 text-[11px]">
            <Activity className="w-3.5 h-3.5 text-purple-400" />
            <span>Intercept (β₀)</span>
          </div>
          <p className="text-lg font-mono font-bold text-purple-400">
            {data.regression.intercept >= 0 ? '+' : ''}
            {data.regression.intercept.toFixed(4)}°C
          </p>
          <p className="text-[10px] text-slate-400">Baseline ΔLST</p>
        </div>

        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 space-y-1">
          <div className="flex items-center space-x-1 text-slate-400 text-[11px]">
            <Database className="w-3.5 h-3.5 text-sky-400" />
            <span>Sample Size (N)</span>
          </div>
          <p className="text-lg font-mono font-bold text-sky-400">
            {data.sample_size.toLocaleString()}
          </p>
          <p className="text-[10px] text-slate-400">Valid 30m pairs</p>
        </div>
      </div>

      {/* 4. SCATTER PLOT */}
      <ScatterPlot
        points={data.scatter_points}
        slope={data.regression.slope}
        intercept={data.regression.intercept}
        rSquared={data.regression.r_squared}
        pearsonR={data.correlation.pearson_r}
      />

      {/* 5. KEY FINDINGS SUMMARY CARD */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-2">
        <div className="flex items-center space-x-2 font-semibold text-white text-xs border-b border-slate-800 pb-2">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <span>Key Findings Summary</span>
        </div>
        <ul className="space-y-1.5 text-xs text-slate-300">
          <li className="flex items-start space-x-2">
            <span className="text-cyan-400 font-bold">•</span>
            <span>
              Spatial ΔNDBI and ΔLST show a{' '}
              <strong className="text-white">
                {isPositive ? 'weak positive' : isNegative ? 'weak negative' : 'minimal'}
              </strong>{' '}
              linear association across {data.location}.
            </span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-emerald-400 font-bold">•</span>
            <span>
              Pearson correlation coefficient{' '}
              <strong className="font-mono text-emerald-400">
                r = {data.correlation.pearson_r >= 0 ? '+' : ''}
                {data.correlation.pearson_r.toFixed(4)}
              </strong>
              {data.correlation.pearson_p_value != null && (
                <span className="text-slate-400 font-mono text-[11px]">
                  {' '}
                  (p = {data.correlation.pearson_p_value.toExponential(2)})
                </span>
              )}
              .
            </span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-cyan-400 font-bold">•</span>
            <span>
              Spearman rank correlation coefficient{' '}
              <strong className="font-mono text-cyan-400">
                ρ = {data.correlation.spearman_rho >= 0 ? '+' : ''}
                {data.correlation.spearman_rho.toFixed(4)}
              </strong>
              {data.correlation.spearman_p_value != null && (
                <span className="text-slate-400 font-mono text-[11px]">
                  {' '}
                  (p = {data.correlation.spearman_p_value.toExponential(2)})
                </span>
              )}
              .
            </span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-amber-400 font-bold">•</span>
            <span>
              The simple OLS linear model has coefficient of determination{' '}
              <strong className="font-mono text-amber-400">
                R² = {data.regression.r_squared.toFixed(4)}
              </strong>
              , indicating that built-up expansion index change explains approximately{' '}
              <strong className="text-white">
                {(data.regression.r_squared * 100).toFixed(2)}%
              </strong>{' '}
              of the observed land surface temperature change variation.
            </span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-red-400 font-bold">•</span>
            <span>
              The statistical relationship demonstrates exploratory spatial association and{' '}
              <strong className="text-red-300">does not demonstrate causality</strong>.
            </span>
          </li>
        </ul>
      </div>

      {/* 6. AUTOMATED INTERPRETATION, CAUSALITY & AUTOCORRELATION WARNINGS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        {/* Interpretation */}
        <div className="bg-cyan-950/30 border border-cyan-500/20 rounded-xl p-4 space-y-1.5 text-cyan-200">
          <div className="flex items-center space-x-1.5 font-semibold text-cyan-400">
            <Info className="w-4 h-4 flex-shrink-0" />
            <span>Automated Interpretation</span>
          </div>
          <p className="text-[11px] leading-relaxed text-slate-300">
            {data.interpretation}
          </p>
        </div>

        {/* Causality Warning */}
        <div className="bg-red-950/30 border border-red-500/20 rounded-xl p-4 space-y-1.5 text-red-200">
          <div className="flex items-center space-x-1.5 font-semibold text-red-400">
            <ShieldAlert className="w-4 h-4 flex-shrink-0" />
            <span>Correlation Does Not Imply Causation</span>
          </div>
          <p className="text-[11px] leading-relaxed text-slate-300">
            These results describe spatial association between observed changes in built-up index and land-surface temperature. They do not demonstrate that urban expansion caused the observed temperature changes.
          </p>
        </div>

        {/* Spatial Autocorrelation Disclosure */}
        <div className="bg-amber-950/30 border border-amber-500/20 rounded-xl p-4 space-y-1.5 text-amber-200">
          <div className="flex items-center space-x-1.5 font-semibold text-amber-400">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>Spatial Autocorrelation Disclosure</span>
          </div>
          <p className="text-[11px] leading-relaxed text-slate-300">
            {data.autocorrelation_warning}
          </p>
        </div>
      </div>

      {/* 7. COLLAPSIBLE METHODOLOGY SECTION */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
        <button
          onClick={() => setShowMethodology(!showMethodology)}
          className="w-full p-4 flex items-center justify-between text-xs font-semibold text-white hover:bg-slate-800/40 transition-colors"
        >
          <div className="flex items-center space-x-2">
            <BookOpen className="w-4 h-4 text-cyan-400" />
            <span>Scientific Methodology & Formulas</span>
          </div>
          {showMethodology ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </button>

        {showMethodology && (
          <div className="p-4 pt-0 border-t border-slate-800/80 space-y-3 text-xs text-slate-300">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-3">
              <div className="space-y-1.5">
                <h5 className="font-semibold text-cyan-400">Normalized Difference Built-up Index (NDBI)</h5>
                <p className="text-[11px] leading-relaxed text-slate-400">
                  Calculated from Sentinel-2 Surface Reflectance Harmonized (<code className="font-mono text-cyan-300">COPERNICUS/S2_SR_HARMONIZED</code>):
                </p>
                <code className="block bg-slate-950 p-2 rounded text-[11px] font-mono text-cyan-300">
                  NDBI = (B11_SWIR1 - B8_NIR) / (B11_SWIR1 + B8_NIR)
                </code>
                <p className="text-[11px] text-slate-400">
                  Native resolution: 20m. Resampled via bilinear interpolation to the 30m projected UTM analysis grid.
                </p>
              </div>

              <div className="space-y-1.5">
                <h5 className="font-semibold text-amber-400">Land Surface Temperature (LST)</h5>
                <p className="text-[11px] leading-relaxed text-slate-400">
                  Derived from Landsat Collection 2 Level-2 thermal band <code className="font-mono text-amber-300">ST_B10</code> (<code className="font-mono text-amber-300">LANDSAT/LC08/C02/T1_L2</code>):
                </p>
                <code className="block bg-slate-950 p-2 rounded text-[11px] font-mono text-amber-300">
                  LST (°C) = (ST_B10 × 0.00341802 + 149.0) − 273.15
                </code>
                <p className="text-[11px] text-slate-400">
                  Native resolution: 30m. Evaluated directly on native thermal grid.
                </p>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800/60 space-y-1.5">
              <h5 className="font-semibold text-emerald-400">Spatial Pairing & OLS Model</h5>
              <p className="text-[11px] leading-relaxed text-slate-400">
                Paired observations are evaluated directly inside Google Earth Engine using random spatial sampling on a projected UTM Zone 44N metric grid (<code className="font-mono text-emerald-300">EPSG:32644</code>) at 30-meter resolution over N = {data.sample_size.toLocaleString()} points.
              </p>
              <code className="block bg-slate-950 p-2 rounded text-[11px] font-mono text-emerald-300">
                ΔLST = β₀ + β₁ × ΔNDBI
              </code>
            </div>
          </div>
        )}
      </div>

      {/* 8. SCIENTIFIC LIMITATIONS SECTION */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-2">
        <div className="flex items-center space-x-2 font-semibold text-slate-200 text-xs">
          <Info className="w-4 h-4 text-slate-400" />
          <span>Scientific Limitations & Methodological Disclosures</span>
        </div>
        <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] text-slate-400">
          <li className="flex items-start space-x-2">
            <span className="text-slate-500 font-bold">•</span>
            <span>Pixel observations may exhibit spatial autocorrelation across adjacent pixels.</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-slate-500 font-bold">•</span>
            <span>The analysis is purely observational and does not establish causality.</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-slate-500 font-bold">•</span>
            <span>NDBI is a spectral proxy for built-up surface intensity, not direct construction data.</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-slate-500 font-bold">•</span>
            <span>LST represents land-surface skin temperature, not near-surface ambient air temperature.</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-slate-500 font-bold">•</span>
            <span>Results depend on satellite cloud masking, compositing, ROI bounds, and selected years.</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-slate-500 font-bold">•</span>
            <span>Single-variable regression does not account for vegetation, elevation, soil moisture, or weather.</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-slate-500 font-bold">•</span>
            <span>Analysis evaluates 2016 and 2025 endpoint composites rather than an annual continuous series.</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
