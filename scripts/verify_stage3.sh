#!/usr/bin/env bash
set -e

echo "=========================================="
echo "  ATLAS-EO Stage 3 Verification Suite     "
echo "=========================================="

python3 -c "
import json
import sys
from pathlib import Path
from src.application.pipeline.research_pipeline import ResearchPipeline

print('[1/5] Initializing Research Pipeline...')
pipeline = ResearchPipeline()

question = 'How has urban expansion affected land surface temperature in Hyderabad between 2016 and 2025?'
print(f'[2/5] Executing full research pipeline for question: \"{question}\"...')

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

project_dir = Path(result.get('project_dir'))
print(f'✅ Pipeline Completed. Project Directory: {project_dir}')

# Read evidence items & verified claims from pipeline context/metadata
print('\n[3/5] Inspecting Stage 3 Retrieved Literature...')
report_md_path = project_dir / 'report.md'
if not report_md_path.exists():
    print(f'❌ Report file not found at: {report_md_path}')
    sys.exit(1)

report_text = report_md_path.read_text(encoding='utf-8')

print('\n========== GENERATED REPORT HEADERS ==========\n')
print('\n'.join(report_text.splitlines()[:30]))
print('\n==============================================\n')

# 4. Print first citation
print('[4/5] Checking Citations & References in Generated Report...')
references = [line for line in report_text.splitlines() if line.startswith('[') or 'DOI:' in line]
for ref in references[:3]:
    print(f'  Reference: {ref}')

# 5. Search for placeholder strings
print('\n[5/5] Auditing Generated Report for Placeholder Evidence...')
placeholders = ['ATLAS Team', 'Satellite Remote Sensing Methodologies', 'NDVI trend verified']
found_placeholders = [p for p in placeholders if p in report_text]

if found_placeholders:
    print(f'❌ Verification Failed! Remaining placeholder strings detected in report: {found_placeholders}')
    sys.exit(1)

print('✅ No placeholder strings detected in generated report!')
print('==========================================')
print('  ✅ Stage 3 Verification Passed!         ')
print('==========================================')
"
