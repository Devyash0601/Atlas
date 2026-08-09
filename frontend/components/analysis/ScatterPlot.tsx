'use client';

import React, { useState } from 'react';
import { ScatterPoint } from '@/lib/api';

interface ScatterPlotProps {
  points: ScatterPoint[];
  slope: number;
  intercept: number;
  rSquared: number;
  pearsonR: number;
}

export default function ScatterPlot({
  points,
  slope,
  intercept,
  rSquared,
  pearsonR,
}: ScatterPlotProps) {
  const [hoveredPoint, setHoveredPoint] = useState<ScatterPoint | null>(null);

  if (!points || points.length === 0) {
    return (
      <div className="w-full h-80 bg-slate-900/60 rounded-xl border border-slate-800 flex items-center justify-center text-xs text-slate-500">
        No scatter points available for display.
      </div>
    );
  }

  // Calculate domain boundaries with padding
  const xValues = points.map((p) => p.delta_ndbi);
  const yValues = points.map((p) => p.delta_lst);

  const rawMinX = Math.min(...xValues);
  const rawMaxX = Math.max(...xValues);
  const rawMinY = Math.min(...yValues);
  const rawMaxY = Math.max(...yValues);

  const paddingX = Math.max(0.05, (rawMaxX - rawMinX) * 0.08);
  const paddingY = Math.max(1.0, (rawMaxY - rawMinY) * 0.08);

  const minX = rawMinX - paddingX;
  const maxX = rawMaxX + paddingX;
  const minY = rawMinY - paddingY;
  const maxY = rawMaxY + paddingY;

  // ViewBox layout dimensions
  const svgWidth = 650;
  const svgHeight = 360;
  const marginTop = 30;
  const marginRight = 30;
  const marginBottom = 55;
  const marginLeft = 65;

  const plotWidth = svgWidth - marginLeft - marginRight;
  const plotHeight = svgHeight - marginTop - marginBottom;

  const scaleX = (val: number) => marginLeft + ((val - minX) / (maxX - minX)) * plotWidth;
  const scaleY = (val: number) => svgHeight - marginBottom - ((val - minY) / (maxY - minY)) * plotHeight;

  // Calculate OLS Regression Line endpoints
  const lineX1 = minX;
  const lineY1 = intercept + slope * minX;
  const lineX2 = maxX;
  const lineY2 = intercept + slope * maxX;

  // Ticks generation
  const xTickCount = 5;
  const yTickCount = 5;

  const xTicks = Array.from({ length: xTickCount }, (_, i) => minX + (i * (maxX - minX)) / (xTickCount - 1));
  const yTicks = Array.from({ length: yTickCount }, (_, i) => minY + (i * (maxY - minY)) / (yTickCount - 1));

  return (
    <div className="relative w-full bg-[#0d1322] border border-slate-800 rounded-xl p-4 shadow-xl space-y-2">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
        <h4 className="text-xs font-semibold text-white flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
          <span>Paired Spatial Observations Scatter Plot (N = {points.length} Viz Sample)</span>
        </h4>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
          30m Analysis Grid
        </span>
      </div>

      <div className="relative w-full overflow-hidden">
        <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="w-full h-auto select-none">
          {/* Background Grid Lines */}
          {xTicks.map((tick, i) => (
            <line
              key={`x-grid-${i}`}
              x1={scaleX(tick)}
              y1={marginTop}
              x2={scaleX(tick)}
              y2={svgHeight - marginBottom}
              stroke="#1e293b"
              strokeDasharray="3 3"
              strokeWidth="1"
            />
          ))}
          {yTicks.map((tick, i) => (
            <line
              key={`y-grid-${i}`}
              x1={marginLeft}
              y1={scaleY(tick)}
              x2={svgWidth - marginRight}
              y2={scaleY(tick)}
              stroke="#1e293b"
              strokeDasharray="3 3"
              strokeWidth="1"
            />
          ))}

          {/* Axes */}
          <line
            x1={marginLeft}
            y1={svgHeight - marginBottom}
            x2={svgWidth - marginRight}
            y2={svgHeight - marginBottom}
            stroke="#475569"
            strokeWidth="1.5"
          />
          <line
            x1={marginLeft}
            y1={marginTop}
            x2={marginLeft}
            y2={svgHeight - marginBottom}
            stroke="#475569"
            strokeWidth="1.5"
          />

          {/* X Axis Ticks & Labels */}
          {xTicks.map((tick, i) => (
            <g key={`x-tick-${i}`} transform={`translate(${scaleX(tick)}, ${svgHeight - marginBottom})`}>
              <line y2="5" stroke="#475569" strokeWidth="1.5" />
              <text y="20" textAnchor="middle" fill="#94a3b8" fontSize="10" fontFamily="monospace">
                {tick.toFixed(2)}
              </text>
            </g>
          ))}

          {/* Y Axis Ticks & Labels */}
          {yTicks.map((tick, i) => (
            <g key={`y-tick-${i}`} transform={`translate(${marginLeft}, ${scaleY(tick)})`}>
              <line x2="-5" stroke="#475569" strokeWidth="1.5" />
              <text x="-10" y="3" textAnchor="end" fill="#94a3b8" fontSize="10" fontFamily="monospace">
                {tick.toFixed(1)}°C
              </text>
            </g>
          ))}

          {/* Axis Titles */}
          <text
            x={marginLeft + plotWidth / 2}
            y={svgHeight - 12}
            textAnchor="middle"
            fill="#e2e8f0"
            fontSize="11"
            fontWeight="500"
          >
            ΔNDBI (Built-up Expansion Index Change, 2016 → 2025)
          </text>
          <text
            transform={`rotate(-90)`}
            x={-(marginTop + plotHeight / 2)}
            y={18}
            textAnchor="middle"
            fill="#e2e8f0"
            fontSize="11"
            fontWeight="500"
          >
            ΔLST (°C Surface Temperature Change)
          </text>

          {/* Scatter Points */}
          {points.map((p, idx) => (
            <circle
              key={`pt-${idx}`}
              cx={scaleX(p.delta_ndbi)}
              cy={scaleY(p.delta_lst)}
              r={2.5}
              className="transition-all duration-150 hover:r-4 cursor-pointer"
              fill="#38bdf8"
              fillOpacity={0.6}
              stroke="#0284c7"
              strokeWidth="0.5"
              onMouseEnter={() => setHoveredPoint(p)}
              onMouseLeave={() => setHoveredPoint(null)}
            />
          ))}

          {/* OLS Linear Regression Trend Line */}
          <line
            x1={scaleX(lineX1)}
            y1={scaleY(lineY1)}
            x2={scaleX(lineX2)}
            y2={scaleY(lineY2)}
            stroke="#ef4444"
            strokeWidth="2.5"
            strokeDasharray="5 3"
          />
        </svg>

        {/* Floating Tooltip */}
        {hoveredPoint && (
          <div className="absolute top-4 right-4 bg-slate-900/90 border border-cyan-500/40 rounded-lg px-3 py-1.5 shadow-2xl text-[11px] font-mono text-white pointer-events-none space-y-0.5">
            <p className="text-cyan-400 font-semibold">Paired Pixel Observation</p>
            <p>ΔNDBI: {hoveredPoint.delta_ndbi.toFixed(4)}</p>
            <p>ΔLST: {hoveredPoint.delta_lst.toFixed(2)} °C</p>
          </div>
        )}
      </div>

      {/* Regression Legend */}
      <div className="flex items-center justify-between bg-slate-900/80 border border-slate-800 rounded-lg px-3 py-2 text-xs">
        <div className="flex items-center space-x-2">
          <span className="w-6 h-0.5 bg-red-500 border border-dashed border-red-400"></span>
          <span className="text-slate-300 font-medium">OLS Regression Line:</span>
          <span className="font-mono text-red-400">
            ΔLST = {slope >= 0 ? '+' : ''}
            {slope.toFixed(2)} × ΔNDBI {intercept >= 0 ? '+' : ''}
            {intercept.toFixed(2)} °C
          </span>
        </div>
        <div className="flex items-center space-x-3 text-[11px] font-mono text-slate-400">
          <span>
            Pearson r: <strong className="text-emerald-400">{pearsonR.toFixed(4)}</strong>
          </span>
          <span>
            R²: <strong className="text-amber-400">{rSquared.toFixed(4)}</strong>
          </span>
        </div>
      </div>
    </div>
  );
}
