'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Play, CheckCircle2, Clock, Terminal, Sliders, AlertCircle, Map, Layers, TrendingUp } from 'lucide-react';
import WorkflowGraph from '@/components/WorkflowGraph';
import MapViewer from '@/components/MapViewer';
import RelationshipAnalysis from '@/components/analysis/RelationshipAnalysis';
import { apiClient } from '@/lib/api';

function ResearchContent() {
  const searchParams = useSearchParams();
  const [question, setQuestion] = useState<string>(
    'How has urban expansion affected land surface temperature in Hyderabad between 2016 and 2025?'
  );
  const [location, setLocation] = useState<string>('Hyderabad, India');
  const [startDate, setStartDate] = useState<string>('2016-01-01');
  const [endDate, setEndDate] = useState<string>('2025-12-31');
  const [cloudThreshold, setCloudThreshold] = useState<number>(20.0);
  const [dataset, setDataset] = useState<string>('COPERNICUS/S2_SR_HARMONIZED');

  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [currentStageIndex, setCurrentStageIndex] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [completedProjectId, setCompletedProjectId] = useState<string | null>(null);

  useEffect(() => {
    const qParam = searchParams.get('question');
    const locParam = searchParams.get('location');
    if (qParam) setQuestion(qParam);
    if (locParam) setLocation(locParam);
  }, [searchParams]);

  const stages = [
    '1. Research Question Validation',
    '2. Research Planning',
    '3. Literature Retrieval',
    '4. Evidence Verification',
    '5. Workflow Graph Construction',
    '6. Earth Engine Plan Generation',
    '7. Earth Engine Execution',
    '8. Result Processing',
    '9. Publication Engine',
    '10. Evaluation Metrics',
    '11. Project Export',
  ];

  const handleStartResearch = async () => {
    setErrorMessage(null);
    setCompletedProjectId(null);
    setIsExecuting(true);
    setCurrentStageIndex(1);

    const interval = setInterval(() => {
      setCurrentStageIndex((prev) => (prev < 10 ? prev + 1 : prev));
    }, 1500);

    try {
      const res = await apiClient.createResearch({
        question,
        location,
        start_date: startDate,
        end_date: endDate,
        dataset_preference: dataset,
      });

      clearInterval(interval);
      setCurrentStageIndex(11);
      setCompletedProjectId(res.project_id);
    } catch (err: any) {
      clearInterval(interval);
      setErrorMessage(err.message || 'Failed to execute research pipeline.');
    } finally {
      setIsExecuting(false);
    }
  };

  const startYear = parseInt(startDate.slice(0, 4)) || 2016;
  const endYear = parseInt(endDate.slice(0, 4)) || 2025;

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Workspace Page Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Research Execution Workspace</h1>
          <p className="text-xs text-slate-400">
            Interactive Earth Observation analysis dashboard: Sentinel-2 NDBI & Landsat LST
          </p>
        </div>
      </div>

      {errorMessage && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center space-x-3 text-xs text-red-400">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* A. Research Query & Control Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form Column */}
        <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-4 shadow-xl">
          <div className="flex items-center space-x-2 text-xs font-semibold text-white pb-2 border-b border-slate-800">
            <Sliders className="w-4 h-4 text-blue-400" />
            <span>Investigation Parameters</span>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-300">Research Question</label>
            <textarea
              rows={3}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-300">Study Location</label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">End Date</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">Max Cloud Cover (%)</label>
              <input
                type="number"
                min={0}
                max={100}
                value={cloudThreshold}
                onChange={(e) => setCloudThreshold(parseFloat(e.target.value) || 0)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">Satellite Dataset</label>
              <select
                value={dataset}
                onChange={(e) => setDataset(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-blue-500"
              >
                <option value="COPERNICUS/S2_SR_HARMONIZED">Sentinel-2 MSI (10m)</option>
                <option value="LANDSAT/LC08/C02/T1_L2">Landsat 8/9 L2 (30m)</option>
                <option value="MODIS/061/MOD13Q1">MODIS (250m)</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleStartResearch}
            disabled={isExecuting}
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold flex items-center justify-center space-x-2 transition-colors shadow-md shadow-blue-600/20"
          >
            <Play className="w-4 h-4" />
            <span>{isExecuting ? 'Executing Pipeline...' : 'Start Research Pipeline'}</span>
          </button>
        </div>

        {/* Live Execution Timeline */}
        <div className="lg:col-span-2 bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-4 flex flex-col justify-between shadow-xl">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <Terminal className="w-4 h-4 text-emerald-400" />
                <h3 className="text-xs font-semibold text-white">Live Execution Progress</h3>
              </div>
              <span className="text-[11px] font-mono text-slate-400">
                {currentStageIndex} / 11 Stages
              </span>
            </div>

            <div className="py-4 space-y-2">
              <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-blue-600 h-full transition-all duration-300"
                  style={{ width: `${(currentStageIndex / 11) * 100}%` }}
                />
              </div>
            </div>

            <div className="space-y-1.5 max-h-[300px] overflow-y-auto pr-1 text-xs">
              {stages.map((stg, idx) => {
                const stageNum = idx + 1;
                const isCompleted = stageNum <= currentStageIndex;
                const isCurrent = stageNum === currentStageIndex && isExecuting;

                return (
                  <div
                    key={idx}
                    className={`flex items-center justify-between p-2 rounded border transition-colors ${
                      isCurrent
                        ? 'bg-blue-600/10 border-blue-500/30 text-white font-medium'
                        : isCompleted
                        ? 'bg-slate-900/60 border-slate-800 text-slate-300'
                        : 'bg-slate-950/40 border-slate-900 text-slate-600'
                    }`}
                  >
                    <span className="truncate">{stg}</span>
                    {isCompleted ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                    ) : isCurrent ? (
                      <Clock className="w-4 h-4 text-blue-400 animate-spin flex-shrink-0" />
                    ) : (
                      <span className="text-[10px] text-slate-600">Pending</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {!isExecuting && completedProjectId && (
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg flex items-center justify-between text-xs text-emerald-400">
              <span>Pipeline execution complete! Package {completedProjectId} created.</span>
              <div className="flex items-center space-x-3">
                <Link href={`/metrics?project_id=${completedProjectId}`} className="underline font-semibold">
                  View Metrics
                </Link>
                <Link href={`/reports/${completedProjectId}`} className="underline font-semibold">
                  View Report
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* B. Workflow Graph Section */}
      <WorkflowGraph />

      {/* C. Interactive Earth Observation Map Section */}
      <div className="space-y-3">
        <div className="flex items-center space-x-2 border-b border-slate-800/80 pb-2">
          <Map className="w-4 h-4 text-cyan-400" />
          <h2 className="text-sm font-bold text-white tracking-wide">
            Interactive Earth Observation Satellite Imagery & Layer Viewer
          </h2>
        </div>
        <MapViewer
          location={location}
          startDate={startDate}
          endDate={endDate}
          cloudThreshold={cloudThreshold}
        />
      </div>

      {/* D. Spatial Relationship & Findings Dashboard Section */}
      <div className="space-y-3 pt-4">
        <div className="flex items-center space-x-2 border-b border-slate-800/80 pb-2">
          <TrendingUp className="w-4 h-4 text-cyan-400" />
          <h2 className="text-sm font-bold text-white tracking-wide">
            Spatial Relationship & Research Findings Dashboard
          </h2>
        </div>
        <RelationshipAnalysis
          location={location}
          startYear={startYear}
          endYear={endYear}
          cloudThreshold={cloudThreshold}
        />
      </div>
    </div>
  );
}

export default function ResearchPage() {
  return (
    <Suspense fallback={<div className="p-8 text-xs text-slate-400">Loading research workspace...</div>}>
      <ResearchContent />
    </Suspense>
  );
}
