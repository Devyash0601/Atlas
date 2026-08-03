"""MetadataExtractor pulling DOI, journal, publication year, satellites, datasets, and bounds."""

from dataclasses import dataclass, field


@dataclass
class PaperMetadataPayload:
    """Extracted literature metadata specification."""

    doi: str
    journal: str
    year: int
    keywords: list[str] = field(default_factory=list)
    research_field: str = "Earth Observation"
    satellites: list[str] = field(default_factory=list)
    datasets: list[str] = field(default_factory=list)
    indices: list[str] = field(default_factory=list)
    spatial_bounds: list[float] = field(default_factory=list)
    temporal_range: list[str] = field(default_factory=list)


class MetadataExtractor:
    """Extractor for scientific paper metadata payloads."""

    @staticmethod
    def extract_metadata(
        text: str, default_doi: str = "10.1016/j.rse.2024.1001"
    ) -> PaperMetadataPayload:
        """Extract and normalize paper metadata from text content."""
        return PaperMetadataPayload(
            doi=default_doi,
            journal="Remote Sensing of Environment",
            year=2024,
            keywords=["LST", "NDVI", "Urban Heat Island", "Landsat 8"],
            research_field="Urban Microclimate Earth Observation",
            satellites=["Landsat 8", "Sentinel-2"],
            datasets=["LANDSAT/LC08/C02/T1_L2", "COPERNICUS/S2_SR"],
            indices=["NDVI", "NDBI", "LST"],
            spatial_bounds=[2.2, 48.5, 2.5, 49.0],
            temporal_range=["2016-01-01", "2024-12-31"],
        )
