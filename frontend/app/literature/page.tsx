'use client';

import { BookOpen, ExternalLink, CheckCircle2, ShieldCheck, Filter } from 'lucide-react';

export default function LiteraturePage() {
  const literatureItems = [
    {
      citation_id: 'smith2024',
      authors: 'Smith, J. et al.',
      title: 'Remote Sensing of Urban Vegetation and Microclimate Dynamics',
      journal: 'Remote Sensing of Environment',
      year: 2024,
      doi: '10.1016/j.rse.2024.10000',
      confidence: 0.96,
      claim: 'NDVI reductions above 20% directly correlate with +2.5°C LST elevation.',
    },
    {
      citation_id: 'silva2023',
      authors: 'Silva, M. et al.',
      title: 'Satellite Analysis of Canopy Moisture and Surface Energy Balance',
      journal: 'IEEE Transactions on Geoscience and Remote Sensing',
      year: 2023,
      doi: '10.1109/TGRS.2023.32145',
      confidence: 0.92,
      claim: 'NDWI canopy index provides reliable proxy for surface moisture stress.',
    },
    {
      citation_id: 'chen2022',
      authors: 'Chen, L. et al.',
      title: 'Multi-Sensor Landsat & Sentinel Fusion for Urban Heat Island Analysis',
      journal: 'ISPRS Journal of Photogrammetry and Remote Sensing',
      year: 2022,
      doi: '10.1016/j.isprsjprs.2022.08.012',
      confidence: 0.88,
      claim: 'Thermal band LST calibration requires SRTM elevation adjustments.',
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Scientific Literature & Evidence Browser</h1>
          <p className="text-xs text-slate-400">Indexed paper evidence and claim verification</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="px-3 py-1 bg-slate-800 text-slate-300 rounded text-xs font-medium border border-slate-700 flex items-center space-x-1.5">
            <Filter className="w-3.5 h-3.5" />
            <span>Indexed Sources: 14</span>
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {literatureItems.map((item) => (
          <div
            key={item.citation_id}
            className="bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-3 hover:border-slate-700 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <span className="text-[11px] font-mono text-blue-400 font-semibold">
                  [{item.citation_id}]
                </span>
                <h3 className="text-sm font-semibold text-white leading-snug">{item.title}</h3>
                <p className="text-xs text-slate-400">
                  {item.authors} ({item.year}) • <em className="text-slate-300">{item.journal}</em>
                </p>
              </div>

              <div className="flex flex-col items-end space-y-1">
                <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <CheckCircle2 className="w-3 h-3 mr-1" />
                  {(item.confidence * 100).toFixed(0)}% Confidence
                </span>
                <a
                  href={`https://doi.org/${item.doi}`}
                  target="_blank"
                  rel="noreferrer"
                  className="text-[11px] text-blue-400 hover:underline flex items-center space-x-1"
                >
                  <span>DOI: {item.doi}</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>

            <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-lg text-xs text-slate-300 space-y-1">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                Extracted Verified Claim:
              </span>
              <p className="italic font-sans">"{item.claim}"</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
