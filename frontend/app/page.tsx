'use client';

import Link from 'next/link';
import { ArrowRight, BookOpen, Cpu, Database, FolderGit2, Layers, Search, ShieldCheck } from 'lucide-react';
import MetricCard from '@/components/MetricCard';

export default function HomePage() {
  const exampleQuestions = [
    {
      q: 'How has urban expansion affected land surface temperature in Hyderabad between 2016 and 2025?',
      loc: 'Hyderabad, India',
      dataset: 'Sentinel-2 / Landsat 8',
    },
    {
      q: 'How did the Assam flood extent evolve during 2022 monsoon season?',
      loc: 'Assam, India',
      dataset: 'Sentinel-1 SAR / MODIS',
    },
    {
      q: 'How has forest canopy cover changed in the Western Ghats between 2015 and 2025?',
      loc: 'Western Ghats, India',
      dataset: 'Landsat 8 / SRTM DEM',
    },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Banner */}
      <section className="bg-gradient-to-r from-blue-950/60 via-slate-900 to-slate-950 border border-blue-500/20 rounded-2xl p-8 relative overflow-hidden">
        <div className="max-w-3xl space-y-4 relative z-10">
          <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
            Autonomous Earth Observation Science Laboratory
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-white tracking-tight leading-tight">
            Trustworthy, Autonomous Earth Observation Research Execution
          </h1>
          <p className="text-slate-300 text-sm leading-relaxed">
            ATLAS-EO executes end-to-end scientific investigations from natural language questions.
            Integrating Scientific RAG, Ollama local LLM runtime, DAG Workflow engine, Google Earth Engine,
            and publication-grade document generation.
          </p>
          <div className="pt-2 flex items-center space-x-4">
            <Link
              href="/research"
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-2 transition-colors shadow-lg shadow-blue-600/20"
            >
              <span>Launch Research Workspace</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/about"
              className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold transition-colors border border-slate-700"
            >
              Architecture & Docs
            </Link>
          </div>
        </div>
      </section>

      {/* Metrics Row */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Active Models"
          value="qwen2.5-coder:14b"
          description="Local Ollama Inference"
          icon={Cpu}
          badgeText="100% Local"
          badgeType="success"
        />
        <MetricCard
          title="Earth Engine Catalog"
          value="7 Datasets"
          description="Sentinel-2, Landsat, MODIS, ERA5"
          icon={Database}
          badgeText="Declarative"
          badgeType="info"
        />
        <MetricCard
          title="Subsystem Verification"
          value="91 / 91 Tests"
          description="Ruff clean & MyPy clean"
          icon={ShieldCheck}
          badgeText="Passing"
          badgeType="success"
        />
        <MetricCard
          title="Publication Output"
          value="PDF / DOCX / MD"
          description="IEEE & Elsevier Formats"
          icon={BookOpen}
          badgeText="BibTeX Ready"
          badgeType="info"
        />
      </section>

      {/* Recommended Sample Questions */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-white">Recommended Research Enquiries</h2>
          <span className="text-xs text-slate-400">Select to populate workspace</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {exampleQuestions.map((item, idx) => (
            <div
              key={idx}
              className="bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-3 flex flex-col justify-between hover:border-slate-700 transition-all group"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-semibold text-blue-400 uppercase tracking-wider">
                    {item.loc}
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">{item.dataset}</span>
                </div>
                <p className="text-xs font-medium text-slate-200 leading-relaxed group-hover:text-white transition-colors">
                  "{item.q}"
                </p>
              </div>

              <Link
                href={`/research?question=${encodeURIComponent(item.q)}&location=${encodeURIComponent(item.loc)}`}
                className="pt-2 flex items-center text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors"
              >
                <span>Run Investigation</span>
                <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </Link>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
