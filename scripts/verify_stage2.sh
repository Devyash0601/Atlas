#!/usr/bin/env bash
set -e

echo "=========================================="
echo "  ATLAS-EO Stage 2 Verification Suite     "
echo "=========================================="

python3 -c "
import json
import sys
from src.application.pipeline.pipeline_context import PipelineContext
from src.application.pipeline.research_pipeline import ResearchPipeline

print('[1/4] Initializing Research Pipeline...')
pipeline = ResearchPipeline()

question = 'How has urban expansion affected land surface temperature in Hyderabad between 2016 and 2025?'
print(f'[2/4] Executing Stage 2 Research Planning for question: \"{question}\"...')

try:
    result = pipeline.run_research(
        question=question,
        location='Hyderabad',
        start_date='2016-01-01',
        end_date='2025-12-31'
    )
except Exception as err:
    print(f'❌ Pipeline Execution Error: {err}')
    sys.exit(1)

project_dir = result.get('project_dir')
print(f'✅ Pipeline Completed. Project Directory: {project_dir}')

# Read context/research_plan from result state
state = result.get('state')
metrics = result.get('metrics')

print('[3/4] Validating Stage 2 Research Plan Structure...')
# Execute direct Stage 2 planning call to inspect raw and parsed JSON
from src.infrastructure.llm.generation import GenerationRequest
from src.infrastructure.llm.ollama_runtime import OllamaRuntime
from src.infrastructure.llm.prompt_engine import PromptEngine
from src.infrastructure.llm.prompts.research_planner import RESEARCH_PLANNER_SCHEMA_DICT

engine = PromptEngine()
runtime = OllamaRuntime()

package = engine.render_package(
    template_id='research_planner',
    question=question,
    location='Hyderabad',
    start_date='2016-01-01',
    end_date='2025-12-31',
    dataset_preference='COPERNICUS/S2_SR_HARMONIZED'
)

gen_req = GenerationRequest(
    prompt_package=package,
    model_name='qwen2.5-coder:7b',
    request_id='stage2_verification'
)

import asyncio
res = asyncio.run(runtime.generate_json(gen_req, expected_schema=RESEARCH_PLANNER_SCHEMA_DICT))

print('\n========== RAW LLM OUTPUT ==========')
print(res.content)
print('====================================\n')

parsed = res.parsed_json
print('========== PARSED JSON PLAN ==========')
print(json.dumps(parsed, indent=2))
print('======================================\n')

required_keys = ['objective', 'study_area', 'time_range', 'datasets', 'indices', 'gee_operations', 'deliverables']
missing = [k for k in required_keys if k not in parsed]

if missing:
    print(f'❌ Verification Failed! Missing required keys: {missing}')
    sys.exit(1)

print('[4/4] All 7 required schema keys present and validated successfully!')
print('==========================================')
print('  ✅ Stage 2 Verification Passed!         ')
print('==========================================')
"
