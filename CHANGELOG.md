# Changelog

All notable changes to the ATLAS-EO project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-08-10

### Added
- **Real Earth Engine Satellite Layers**:
  - Sentinel-2 Surface Reflectance Harmonized True-Color RGB (`B4`, `B3`, `B2`).
  - Sentinel-2 Normalized Difference Vegetation Index (NDVI: `(B8 - B4) / (B8 + B4)`).
  - Sentinel-2 Normalized Difference Water Index (NDWI: `(B3 - B8) / (B3 + B8)`).
  - Sentinel-2 Normalized Difference Built-up Index (NDBI: `(B11 - B8) / (B11 + B8)`).
  - Landsat 8/9 Thermal Land Surface Temperature (LST: `ST_B10 * 0.00341802 + 149.0 - 273.15` in °C).
- **Change Analysis Engine**:
  - $\Delta\text{NDBI} = \text{NDBI}_{2025} - \text{NDBI}_{2016}$ (Native 20m).
  - $\Delta\text{LST} = \text{LST}_{2025} - \text{LST}_{2016}$ (Native 30m).
- **Projected Metric Grid Spatial Relationship Engine**:
  - Dynamic Universal Transverse Mercator (UTM) projected metric CRS calculation (e.g. `EPSG:32644` UTM Zone 44N for Hyderabad, `EPSG:32643` UTM Zone 43N for Bengaluru & Delhi).
  - In-engine GEE spatial sampling on a common 30m metric grid over $N = 5,000$ paired pixel observations.
  - Pearson correlation $r$, Spearman rank correlation $\rho$, OLS linear regression, and coefficient of fit $R^2$.
  - Independent statistical validation ensuring 0.000000000000e+00 discrepancy between production API and reference calculations on full-precision raw arrays.
- **Research Analysis Dashboard & Interactive UI**:
  - Interactive Leaflet map supporting 9 satellite and change layers with dynamic legends, opacity, and coordinate tracking.
  - Interactive SVG Scatter Plot with 2,000 visualization points, OLS regression trend line, hover tooltips, and dynamic regression equation.
  - Automated interpretation cards, explicit Non-Causality Disclosures, and Spatial Autocorrelation warnings.
  - Collapsible scientific methodology and 7 methodological limitations disclosures.
- **Developer & Production Tooling**:
  - Clean Architecture & DDD backend structure in FastAPI with typed Pydantic V2 schemas.
  - Next.js 15 App Router frontend with TypeScript strict mode.
  - Docker Compose containerized environment (PostgreSQL, Redis, Qdrant, Ollama, FastAPI, Next.js).
  - Automated quality gate suite (`pytest`, `ruff`, `mypy`, `tsc`, `next build`).
