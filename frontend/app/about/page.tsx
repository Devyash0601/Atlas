'use client';

import { BookOpen, CheckCircle2, Cpu, Database, Info, Layers, ShieldCheck } from 'lucide-react';

export default function AboutPage() {
  const documents = [
    { num: '00–26', title: 'System Architecture & Principles', desc: 'Core platform blueprint, domain boundaries, zero paid APIs invariant.' },
    { num: '27', title: 'Block A — AI Runtime', desc: '4-tier memory lifecycle, prompt engine, structured output parser.' },
    { num: '28', title: 'Production Ollama Runtime', desc: 'Model registry, idle unloading, streaming engine, context window manager.' },
    { num: '29', title: 'Production Scientific RAG', desc: 'Semantic chunker, Qdrant vector store, ONNX reranker, hallucination guard.' },
    { num: '30', title: 'Research Workflow Engine', desc: '7-stage DAG topology, artifact store, task router, execution history.' },
    { num: '31', title: 'Production Earth Engine Runtime', desc: 'Declarative GEE plan spec, compiler, executor, 7 dataset catalog.' },
    { num: '32', title: 'Publication Engine', desc: 'Scientific report builder, IEEE/Elsevier layout templates, PDF/DOCX export.' },
    { num: '33', title: 'End-to-End Research Pipeline', desc: '11-stage autonomous orchestration pipeline & CLI.' },
    { num: '34', title: 'Research Workspace Frontend', desc: 'Next.js 15, TailwindCSS, React Flow, MapLibre GL UI.' },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">System Architecture & Specifications</h1>
          <p className="text-xs text-slate-400">ATLAS-EO Technical Documents Index (00–34)</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {documents.map((doc, idx) => (
          <div
            key={idx}
            className="bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-2 hover:border-slate-700 transition-colors"
          >
            <div className="flex items-center justify-between">
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono">
                Doc {doc.num}
              </span>
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <h3 className="text-xs font-semibold text-white leading-snug">{doc.title}</h3>
            <p className="text-[11px] text-slate-400 leading-relaxed">{doc.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
