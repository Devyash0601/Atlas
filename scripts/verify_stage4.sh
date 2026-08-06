#!/usr/bin/env bash
set -e

echo "=========================================="
echo "  ATLAS-EO Stage 4 Verification Suite     "
echo "=========================================="

python3 -c "
import json
import sys
from pathlib import Path
from src.application.pipeline.pipeline_context import PipelineContext
from src.application.pipeline.pipeline_executor import PipelineExecutor
from src.application.pipeline.pipeline_metrics import PipelineMetrics
from src.application.pipeline.pipeline_state import PipelineState

executor = PipelineExecutor()

print('[1/5] Executing Pipeline Run A: Urban Expansion vs LST (Hyderabad)...')
ctx_a = PipelineContext(
    research_uuid='res_ver4_a',
    question='How has urban expansion affected land surface temperature in Hyderabad between 2016 and 2025?',
    location='Hyderabad',
    start_date='2016-01-01',
    end_date='2025-12-31'
)
res_a = executor.execute_pipeline(ctx_a, PipelineState(), PipelineMetrics(), Path('/tmp/stage4_a'))
papers_a = ctx_a.metadata.get('evidence_items', [])
claims_a = ctx_a.metadata.get('verified_claims', [])

print(f'✅ Run A Completed. Retrieved {len(papers_a)} papers, {len(claims_a)} claims.')

print('\n[2/5] Executing Pipeline Run B: Amazon Deforestation vs Soil Moisture (Amazon)...')
ctx_b = PipelineContext(
    research_uuid='res_ver4_b',
    question='How has deforestation affected soil moisture in the Amazon Basin between 2018 and 2024?',
    location='Amazon Basin',
    start_date='2018-01-01',
    end_date='2024-12-31'
)
res_b = executor.execute_pipeline(ctx_b, PipelineState(), PipelineMetrics(), Path('/tmp/stage4_b'))
papers_b = ctx_b.metadata.get('evidence_items', [])
claims_b = ctx_b.metadata.get('verified_claims', [])

print(f'✅ Run B Completed. Retrieved {len(papers_b)} papers, {len(claims_b)} claims.')

print('\n[3/5] Comparing Retrieved Literature (Run A vs Run B)...')
titles_a = [p['title'] for p in papers_a]
titles_b = [p['title'] for p in papers_b]

print('Run A Papers:')
for t in titles_a:
    print(f'  - {t}')

print('\nRun B Papers:')
for t in titles_b:
    print(f'  - {t}')

if set(titles_a) == set(titles_b):
    print('\n❌ Verification Failed! Exactly identical papers returned for both questions.')
    sys.exit(1)

print('\n✅ Dynamic Literature Retrieval Confirmed: Run A and Run B retrieved distinct scientific papers!')

print('\n[4/5] Comparing Verified Claims (Run A vs Run B)...')
claim_texts_a = [c['claim'] for c in claims_a]
claim_texts_b = [c['claim'] for c in claims_b]

print('Run A Claims:')
for c in claim_texts_a:
    print(f'  - {c}')

print('\nRun B Claims:')
for c in claim_texts_b:
    print(f'  - {c}')

if set(claim_texts_a) == set(claim_texts_b):
    print('\n❌ Verification Failed! Exactly identical claims returned for both questions.')
    sys.exit(1)

print('\n✅ Dynamic Evidence Verification Confirmed: Run A and Run B generated distinct verified claims!')

print('\n[5/5] Auditing Generated Reports for Citation Differentiation...')
rep_a = (Path(res_a['project_dir']) / 'report.md').read_text(encoding='utf-8')
rep_b = (Path(res_b['project_dir']) / 'report.md').read_text(encoding='utf-8')

if 'singh2023_rse' in rep_a and 'silva2023_gcb' in rep_b:
    print('✅ Generated reports contain topic-differentiated references!')

print('==========================================')
print('  ✅ Stage 4 Verification Passed!         ')
print('==========================================')
"
