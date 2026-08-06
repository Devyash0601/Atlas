"""BenchmarkDatasetLoader loading benchmark datasets for UHI, Flood, Deforestation."""

from dataclasses import dataclass, field


@dataclass
class BenchmarkItem:
    """Ground truth benchmark item container."""

    benchmark_id: str
    category: str
    question: str
    location: str
    expected_datasets: list[str]
    expected_citations: set[str]
    ground_truth_claims: list[str] = field(default_factory=list)


class BenchmarkDatasetLoader:
    """Loader providing ground-truth benchmark evaluation queries."""

    @staticmethod
    def load_default_benchmarks() -> list[BenchmarkItem]:
        """Return default suite of scientific benchmark datasets."""
        return [
            BenchmarkItem(
                benchmark_id="uhi_hyderabad_2025",
                category="Urban Heat Island",
                question=(
                    "How has urban expansion affected land surface temperature in Hyderabad "
                    "between 2016 and 2025?"
                ),
                location="Hyderabad, India",
                expected_datasets=["COPERNICUS/S2_SR_HARMONIZED", "LANDSAT/LC08/C02/T1_L2"],
                expected_citations={"smith2024", "chen2022"},
                ground_truth_claims=["NDVI reductions correlate with +2.5°C LST elevation"],
            ),
            BenchmarkItem(
                benchmark_id="flood_assam_2022",
                category="Flood Monitoring",
                question="How did the Assam flood extent evolve during 2022?",
                location="Assam, India",
                expected_datasets=["COPERNICUS/S2_SR_HARMONIZED", "MODIS/061/MOD13Q1"],
                expected_citations={"silva2023"},
                ground_truth_claims=["Peak inundation observed in June 2022"],
            ),
            BenchmarkItem(
                benchmark_id="forest_western_ghats_2025",
                category="Deforestation",
                question="How has forest cover changed in the Western Ghats between 2015 and 2025?",
                location="Western Ghats, India",
                expected_datasets=["LANDSAT/LC08/C02/T1_L2"],
                expected_citations={"silva2023"},
                ground_truth_claims=["Canopy cover loss observed along forest margins"],
            ),
        ]
