"""ResearchPlanner PromptTemplate for generating structured Earth Observation research plans."""

from typing import Any

from src.infrastructure.llm.prompt_registry import PromptSchema
from src.infrastructure.llm.prompt_template import PromptTemplate

RESEARCH_PLANNER_SYSTEM_PROMPT = (
    "You are an Earth Observation research planner.\n"
    "Your task is to convert a natural language research question into a "
    "structured scientific research plan.\n"
    "CRITICAL RULES:\n"
    "- Return ONLY valid JSON.\n"
    "- Do NOT return Markdown or explanation.\n"
    "- Do NOT use ```json code fences.\n"
    "- The first character of your response MUST be '{{'.\n"
    "- The last character of your response MUST be '}}'.\n"
    "- EVERY required field listed below MUST exist. Missing fields are not allowed.\n\n"
    "REQUIRED JSON SCHEMA:\n"
    "{{\n"
    '  "objective": "High level research objective string",\n'
    '  "study_area": "Location string",\n'
    '  "time_range": {{\n'
    '    "start": "YYYY-MM-DD",\n'
    '    "end": "YYYY-MM-DD"\n'
    "  }},\n"
    '  "datasets": ["List of satellite dataset IDs"],\n'
    '  "indices": ["List of spectral or climate indices"],\n'
    '  "gee_operations": ["List of Earth Engine processing steps"],\n'
    '  "deliverables": ["List of output deliverables"]\n'
    "}}\n\n"
    "EXAMPLE OUTPUT:\n"
    "{{\n"
    '  "objective": "Analyze the impact of urban expansion on land surface temperature",\n'
    '  "study_area": "Hyderabad, India",\n'
    '  "time_range": {{"start": "2016-01-01", "end": "2025-12-31"}},\n'
    '  "datasets": ["COPERNICUS/S2_SR_HARMONIZED", "LANDSAT/LC08/C02/T1_L2"],\n'
    '  "indices": ["NDVI", "LST"],\n'
    '  "gee_operations": ["LoadCollection", "CloudMask", "NDVI", "LST", "ReduceRegions"],\n'
    '  "deliverables": ["LST Trend Map", "Urban Expansion Time Series", "Scientific Report"]\n'
    "}}"
)

RESEARCH_PLANNER_USER_PROMPT = (
    "Question\n"
    "{question}\n\n"
    "Location\n"
    "{location}\n\n"
    "Start Date\n"
    "{start_date}\n\n"
    "End Date\n"
    "{end_date}\n\n"
    "Dataset Preference\n"
    "{dataset_preference}"
)

RESEARCH_PLANNER_SCHEMA_DICT: dict[str, Any] = {
    "type": "object",
    "required": [
        "objective",
        "study_area",
        "time_range",
        "datasets",
        "indices",
        "gee_operations",
        "deliverables",
    ],
    "properties": {
        "objective": {"type": "string"},
        "study_area": {"type": "string"},
        "time_range": {
            "type": "object",
            "required": ["start", "end"],
            "properties": {
                "start": {"type": "string"},
                "end": {"type": "string"},
            },
        },
        "datasets": {"type": "array", "items": {"type": "string"}},
        "indices": {"type": "array", "items": {"type": "string"}},
        "gee_operations": {"type": "array", "items": {"type": "string"}},
        "deliverables": {"type": "array", "items": {"type": "string"}},
    },
}

RESEARCH_PLANNER_TEMPLATE = PromptTemplate(
    system_template=RESEARCH_PLANNER_SYSTEM_PROMPT,
    user_template=RESEARCH_PLANNER_USER_PROMPT,
)

RESEARCH_PLANNER_SCHEMA = PromptSchema(
    id="research_planner",
    version="1.0",
    description="Generates structured Earth Observation scientific research plans in JSON",
    owner="ATLAS-EO Core",
    input_schema={
        "question": "str",
        "location": "str",
        "start_date": "str",
        "end_date": "str",
        "dataset_preference": "str",
    },
    output_schema=RESEARCH_PLANNER_SCHEMA_DICT,
)
