'use client';

import { Download, Table as TableIcon } from 'lucide-react';

interface TablePanelProps {
  title?: string;
  headers?: string[];
  rows?: Array<Array<string | number>>;
}

export default function TablePanel({
  title = 'Statistical Summary',
  headers = ['Parameter', '2016 Baseline', '2025 Current', 'Delta (%)'],
  rows = [
    ['Mean NDVI', 0.42, 0.31, '-26.2%'],
    ['Mean LST (°C)', 31.5, 34.8, '+10.4%'],
    ['Built-up Area (km²)', 142.0, 218.5, '+53.8%'],
    ['Water Extent (km²)', 24.5, 18.2, '-25.7%'],
  ],
}: TablePanelProps) {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800 bg-[#0f172a] flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <TableIcon className="w-4 h-4 text-indigo-400" />
          <h3 className="text-xs font-semibold text-white">{title}</h3>
        </div>

        <button className="flex items-center space-x-1.5 px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-medium transition-colors">
          <Download className="w-3.5 h-3.5 text-slate-400" />
          <span>Export CSV</span>
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/60 text-slate-400 font-semibold border-b border-slate-800">
            <tr>
              {headers.map((h, i) => (
                <th key={i} className="px-4 py-2.5">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-slate-200">
            {rows.map((r, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-slate-800/40 transition-colors">
                {r.map((val, colIndex) => (
                  <td key={colIndex} className="px-4 py-2.5">
                    {val}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
