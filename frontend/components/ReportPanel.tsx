'use client';

import { useState } from 'react';
import { Download, FileText } from 'lucide-react';

interface ReportPanelProps {
  title?: string;
  question?: string;
  reportContent?: string;
  metadata?: Record<string, any>;
}

export default function ReportPanel({
  title = 'Automated Scientific Earth Observation Report',
  question = 'How has urban expansion affected land surface temperature in Hyderabad between 2016 and 2025?',
  reportContent,
  metadata = {},
}: ReportPanelProps) {
  const [tab, setTab] = useState<'md' | 'html' | 'bib'>('md');

  const defaultMdContent = `# ${title}

**Author**: ATLAS-EO Autonomous Platform | **Style**: IEEE Format

---

# 1. Introduction
Earth Observation satellite analysis provides essential planetary monitoring. This paper addresses the primary research question: **${question}**.

# 2. Results & Discussion
Satellite computations processed multi-band satellite data. Result summary metrics indicate high statistical agreement between thermal infrared and vegetation index reductions.

## References
[1] Smith, J., & Doe, A. (2024). Remote Sensing of Urban Vegetation. Remote Sensing of Environment.
`;

  const mdText = reportContent || defaultMdContent;

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl overflow-hidden flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-800 bg-[#0f172a] flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <FileText className="w-4 h-4 text-blue-400" />
          <h3 className="text-xs font-semibold text-white">Publication Paper Previewer</h3>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setTab('md')}
            className={`px-2.5 py-1 rounded text-xs font-medium ${
              tab === 'md' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400'
            }`}
          >
            Markdown
          </button>
          <button
            onClick={() => setTab('html')}
            className={`px-2.5 py-1 rounded text-xs font-medium ${
              tab === 'html' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400'
            }`}
          >
            HTML
          </button>
          <button
            onClick={() => setTab('bib')}
            className={`px-2.5 py-1 rounded text-xs font-medium ${
              tab === 'bib' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400'
            }`}
          >
            BibTeX
          </button>
        </div>
      </div>

      {/* Report Body */}
      <div className="p-6 bg-[#0b0f19] space-y-4 max-h-[500px] overflow-y-auto font-mono text-xs text-slate-300">
        {tab === 'md' && (
          <pre className="whitespace-pre-wrap font-mono text-xs text-slate-200 leading-relaxed">
            {mdText}
          </pre>
        )}

        {tab === 'html' && (
          <pre className="text-[11px] text-emerald-400 overflow-x-auto whitespace-pre-wrap font-mono">
            {`<!DOCTYPE html>
<html>
<head><title>${title}</title></head>
<body>
  <h1>${title}</h1>
  <p>Research Question: ${question}</p>
</body>
</html>`}
          </pre>
        )}

        {tab === 'bib' && (
          <pre className="text-[11px] text-amber-400 overflow-x-auto whitespace-pre-wrap font-mono">
            {`@article{atlas2026,
  author = {ATLAS-EO Scientific Platform},
  title = {${title}},
  journal = {Earth Observation Research Reports},
  year = {2026},
  publisher = {ATLAS-EO Platform}
}`}
          </pre>
        )}
      </div>

      {/* Export Bar */}
      <div className="px-4 py-3 border-t border-slate-800 bg-[#0f172a] flex items-center justify-between">
        <span className="text-[11px] text-slate-400">
          Status: Verified • Citations: {metadata.citation_count || 3}
        </span>
        <div className="flex items-center space-x-2">
          <button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-semibold flex items-center space-x-1.5 transition-colors">
            <Download className="w-3.5 h-3.5" />
            <span>Download PDF</span>
          </button>
          <button className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-semibold flex items-center space-x-1.5 transition-colors">
            <Download className="w-3.5 h-3.5" />
            <span>DOCX</span>
          </button>
        </div>
      </div>
    </div>
  );
}
