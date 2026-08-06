'use client';

import { useState } from 'react';
import { CheckCircle2, Clock, PlayCircle } from 'lucide-react';

interface NodeItem {
  id: string;
  label: string;
  type: string;
  status: 'COMPLETED' | 'RUNNING' | 'WAITING';
  duration: string;
}

export default function WorkflowGraph() {
  const [selectedNode, setSelectedNode] = useState<string>('node_1');

  const nodes: NodeItem[] = [
    { id: 'node_1', label: '1. Ingest Literature', type: 'Scientific RAG', status: 'COMPLETED', duration: '0.42s' },
    { id: 'node_2', label: '2. Verify Evidence', type: 'Hallucination Guard', status: 'COMPLETED', duration: '0.18s' },
    { id: 'node_3', label: '3. Construct GEE Spec', type: 'Compiler', status: 'COMPLETED', duration: '0.09s' },
    { id: 'node_4', label: '4. Execute Reductions', type: 'Earth Engine Runtime', status: 'COMPLETED', duration: '0.85s' },
    { id: 'node_5', label: '5. Statistical Summary', type: 'Statistics Engine', status: 'COMPLETED', duration: '0.12s' },
    { id: 'node_6', label: '6. Assemble Publication', type: 'Report Builder', status: 'COMPLETED', duration: '0.31s' },
    { id: 'node_7', label: '7. Export Package', type: 'Export Manager', status: 'COMPLETED', duration: '0.15s' },
  ];

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-white">Workflow Directed Acyclic Graph (DAG)</h3>
          <p className="text-xs text-slate-400">7-Stage Autonomous Pipeline Topology</p>
        </div>
        <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          7 / 7 Nodes Completed
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
        {nodes.map((node) => {
          const isSelected = selectedNode === node.id;
          return (
            <button
              key={node.id}
              onClick={() => setSelectedNode(node.id)}
              className={`p-3 rounded-lg border text-left transition-all ${
                isSelected
                  ? 'bg-blue-600/15 border-blue-500/40 shadow-sm shadow-blue-500/10'
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between text-xs mb-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-[10px] text-slate-400">{node.duration}</span>
              </div>
              <p className="font-semibold text-xs text-white truncate">{node.label}</p>
              <p className="text-[10px] text-slate-400">{node.type}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
