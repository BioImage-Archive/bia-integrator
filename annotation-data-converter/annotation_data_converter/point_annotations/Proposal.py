from dataclasses import dataclass
from uuid import UUID
from pathlib import Path

@dataclass
class PointAnnotationProposal:
    annotation_data_uuid: UUID
    image_representation_uuid: UUID
    mode: str
    x: str | int
    y: str | int
    z: str | int
    filter_column: str | None = None
    filter_value: str | None = None
    local_file_path: Path | None = None


