'use client';

import { Image as ImageIcon, ExternalLink } from 'lucide-react';

interface FigurePanelProps {
  title?: string;
  caption?: string;
  imagePath?: string;
  sourceArtifact?: string;
}

export default function FigurePanel({
  title = 'Figure 1: Normalized Difference Vegetation Index (NDVI) Reduction Map',
  caption = 'False-color reduction map displaying regional canopy moisture and vegetation loss.',
  imagePath = 'figures/ndvi_map.png',
  sourceArtifact = 'art_ee_9001',
}: FigurePanelProps) {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl overflow-hidden space-y-3 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <ImageIcon className="w-4 h-4 text-emerald-400" />
          <h4 className="text-xs font-semibold text-white">{title}</h4>
        </div>
        <span className="text-[10px] text-slate-500 font-mono">Artifact: {sourceArtifact}</span>
      </div>

      <div className="h-48 bg-slate-950 rounded-lg border border-slate-800 flex items-center justify-center relative overflow-hidden">
        <div className="text-center space-y-2 p-4">
          <ImageIcon className="w-8 h-8 text-slate-600 mx-auto" />
          <p className="text-xs text-slate-400">{imagePath}</p>
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300">
            Rendered GeoTIFF Output
          </span>
        </div>
      </div>

      <p className="text-xs text-slate-400 italic">{caption}</p>
    </div>
  );
}
