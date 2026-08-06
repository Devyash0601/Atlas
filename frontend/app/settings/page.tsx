'use client';

import { useState } from 'react';
import { Cpu, Database, Save, Settings as SettingsIcon, ShieldCheck } from 'lucide-react';

export default function SettingsPage() {
  const [model, setModel] = useState<string>('qwen2.5-coder:14b-instruct-q4_K_M');
  const [format, setFormat] = useState<string>('all');
  const [timeout, setTimeoutVal] = useState<number>(600);
  const [cache, setCache] = useState<boolean>(true);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Platform Settings</h1>
          <p className="text-xs text-slate-400">Configure LLM runtime, GEE options, and export preferences</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-colors shadow-md shadow-blue-600/20">
          <Save className="w-3.5 h-3.5" />
          <span>Save Preferences</span>
        </button>
      </div>

      <div className="space-y-6">
        {/* Ollama LLM Settings */}
        <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center space-x-2 text-xs font-semibold text-white pb-2 border-b border-slate-800">
            <Cpu className="w-4 h-4 text-blue-400" />
            <span>Local Ollama LLM Runtime</span>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-300">Model Choice</label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-blue-500"
            >
              <option value="qwen2.5-coder:14b-instruct-q4_K_M">
                qwen2.5-coder:14b-instruct-q4_K_M (Default — 11.0 GB VRAM)
              </option>
              <option value="llama3.1:8b-instruct-q4_K_M">llama3.1:8b-instruct-q4_K_M (Lightweight)</option>
              <option value="deepseek-r1:14b">deepseek-r1:14b (Reasoning Specialist)</option>
            </select>
          </div>
        </div>

        {/* Earth Engine Options */}
        <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center space-x-2 text-xs font-semibold text-white pb-2 border-b border-slate-800">
            <Database className="w-4 h-4 text-emerald-400" />
            <span>Google Earth Engine Runtime</span>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-300">Execution Timeout (Seconds)</label>
            <input
              type="number"
              value={timeout}
              onChange={(e) => setTimeoutVal(parseInt(e.target.value))}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="flex items-center justify-between pt-2">
            <div>
              <p className="text-xs font-medium text-white">Enable Cache Strategy</p>
              <p className="text-[11px] text-slate-400">Reuse previously computed EE reductions for identical plan specs</p>
            </div>
            <input
              type="checkbox"
              checked={cache}
              onChange={(e) => setCache(e.target.checked)}
              className="w-4 h-4 accent-blue-500 rounded"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
