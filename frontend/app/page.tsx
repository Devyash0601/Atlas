'use client';

import { useEffect, useState } from 'react';
import { fetchHealthStatus, HealthData } from '@/lib/api-client';
import { Activity, Shield, Cpu, Database, Map, CheckCircle, AlertCircle } from 'lucide-react';

export default function DashboardPage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHealthStatus()
      .then((res) => {
        setHealth(res.data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to connect to backend API');
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top Header */}
      <header className="border-b border-gray-800 bg-[#0f172a]/80 backdrop-blur sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white shadow-lg shadow-blue-500/20">
            A
          </div>
          <div>
            <h1 className="font-semibold text-lg text-white leading-tight">ATLAS-EO</h1>
            <p className="text-xs text-gray-400">Earth Observation Science Laboratory</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
            V1.0.0 — Phase 1 Repository Foundation
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-8">
        {/* Banner */}
        <section className="bg-gradient-to-r from-blue-900/40 via-slate-900 to-indigo-950/40 border border-blue-500/20 rounded-2xl p-8 relative overflow-hidden">
          <div className="max-w-2xl space-y-3 relative z-10">
            <h2 className="text-3xl font-bold text-white tracking-tight">
              Trustworthy Autonomous Science Platform
            </h2>
            <p className="text-gray-300 text-sm leading-relaxed">
              ATLAS-EO conducts reproducible, transparent, and evidence-verified Earth Observation research.
              Currently operating in V1 mode focused on Urban Heat Island (UHI) analysis.
            </p>
          </div>
        </section>

        {/* Backend Status Card */}
        <section className="space-y-4">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Infrastructure Status</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Backend API Health Card */}
            <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-400">FastAPI Backend</span>
                <Activity className="w-4 h-4 text-blue-400" />
              </div>
              {loading ? (
                <div className="animate-pulse flex space-x-2 items-center text-sm text-gray-500">
                  <span>Connecting to API...</span>
                </div>
              ) : error ? (
                <div className="flex items-center space-x-2 text-sm text-red-400">
                  <AlertCircle className="w-4 h-4" />
                  <span className="text-xs truncate">{error}</span>
                </div>
              ) : (
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                    <span className="font-semibold text-white text-base capitalize">{health?.status}</span>
                  </div>
                  <p className="text-xs text-gray-400">Uptime: {health?.uptime_seconds}s | Env: {health?.environment}</p>
                </div>
              )}
            </div>

            {/* Container Placeholders */}
            <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-400">PostgreSQL 16</span>
                <Database className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-emerald-400" />
                <span className="font-semibold text-white text-sm">Container Ready</span>
              </div>
              <p className="text-xs text-gray-400">Relational System of Record</p>
            </div>

            <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-400">Qdrant Vector DB</span>
                <Shield className="w-4 h-4 text-purple-400" />
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-emerald-400" />
                <span className="font-semibold text-white text-sm">Container Ready</span>
              </div>
              <p className="text-xs text-gray-400">Literature Vector Embeddings</p>
            </div>

            <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-400">Ollama Local LLM</span>
                <Cpu className="w-4 h-4 text-amber-400" />
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-emerald-400" />
                <span className="font-semibold text-white text-sm">Container Ready</span>
              </div>
              <p className="text-xs text-gray-400">Qwen3 8B Local Inference</p>
            </div>
          </div>
        </section>

        {/* Workflow Overview Placeholder */}
        <section className="bg-[#111827] border border-gray-800 rounded-xl p-6 space-y-4">
          <div className="flex items-center space-x-2">
            <Map className="w-5 h-5 text-blue-400" />
            <h3 className="text-base font-semibold text-white">Target Workflow: Urban Heat Island (UHI) Analysis</h3>
          </div>
          <p className="text-xs text-gray-400 max-w-3xl">
            Phase 1 establishes the containerized foundation and API layer. Subsequent phases will integrate Google Earth Engine, Literature RAG, Agent Orchestration, and Automated Scientific Report Generation.
          </p>
        </section>
      </main>
    </div>
  );
}
