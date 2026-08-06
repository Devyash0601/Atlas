#!/usr/bin/env bash
set -e

echo "=========================================="
echo "  ATLAS-EO Stage 5 Verification Suite     "
echo "=========================================="

python3 -c "
import sys
from pathlib import Path
from src.application.pipeline.pipeline_context import PipelineContext
from src.application.pipeline.pipeline_executor import PipelineExecutor
from src.application.pipeline.pipeline_metrics import PipelineMetrics
from src.application.pipeline.pipeline_state import PipelineState

executor = PipelineExecutor()

print('[1/5] Executing Pipeline Run A: Urban Expansion vs LST (Hyderabad)...')
ctx_a = PipelineContext(
    research_uuid='res_ver5_a',
    question='How has urban expansion affected land surface temperature in Hyderabad between 2016 and 2025?',
    location='Hyderabad',
    start_date='2016-01-01',
    end_date='2025-12-31'
)
res_a = executor.execute_pipeline(ctx_a, PipelineState(), PipelineMetrics(), Path('/tmp/stage5_a'))
plan_a = ctx_a.metadata.get('gee_plan')

print(f'✅ Run A Completed. GEE Plan Dataset: {plan_a.target_dataset}')

print('\n[2/5] Executing Pipeline Run B: Amazon Deforestation vs Soil Moisture (Amazon)...')
ctx_b = PipelineContext(
    research_uuid='res_ver5_b',
    question='How has deforestation affected soil moisture in the Amazon Basin between 2018 and 2024?',
    location='Amazon Basin',
    start_date='2018-01-01',
    end_date='2024-12-31'
)
res_b = executor.execute_pipeline(ctx_b, PipelineState(), PipelineMetrics(), Path('/tmp/stage5_b'))
plan_b = ctx_b.metadata.get('gee_plan')

print(f'✅ Run B Completed. GEE Plan Dataset: {plan_b.target_dataset}')

print('\n[3/5] Comparing Dynamic GEE Plan Operations (Run A vs Run B)...')
ops_a = [op.op_type for op in plan_a.operations]
ops_b = [op.op_type for op in plan_b.operations]

print(f'Run A Operations: {ops_a}')
print(f'Run B Operations: {ops_b}')

if ops_a == ops_b:
    print('\n❌ Verification Failed! Identical operations generated for both questions.')
    sys.exit(1)

print('✅ Dynamic GEE Operations Confirmed: Run A and Run B generated distinct operation sequences!')

print('\n[4/5] Comparing Dynamic Spatial Bounds & Temporal Ranges (Run A vs Run B)...')
print(f'Run A Spatial Bounds: {plan_a.spatial_bounds} | Temporal: {plan_a.temporal_range}')
print(f'Run B Spatial Bounds: {plan_b.spatial_bounds} | Temporal: {plan_b.temporal_range}')

if plan_a.spatial_bounds == plan_b.spatial_bounds:
    print('\n❌ Verification Failed! Identical spatial bounds generated for both questions.')
    sys.exit(1)

if plan_a.temporal_range == plan_b.temporal_range:
    print('\n❌ Verification Failed! Identical temporal ranges generated for both questions.')
    sys.exit(1)

print('✅ Dynamic Spatial Bounds & Temporal Ranges Confirmed!')

print('\n[5/5] Auditing GEE Plan Validation & Execution Integration...')
from src.infrastructure.earth_engine_runtime.gee_plan_validator import GEEPlanValidator
validator = GEEPlanValidator()
validator.validate_plan(plan_a)
validator.validate_plan(plan_b)

print('✅ GEE Plan Validation Passed for both dynamic specs!')
print('==========================================')
print('  ✅ Stage 5 Verification Passed!         ')
print('==========================================')
"
