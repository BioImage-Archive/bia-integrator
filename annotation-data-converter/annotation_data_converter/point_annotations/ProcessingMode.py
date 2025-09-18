from dataclasses import dataclass


@dataclass(frozen=True)
class PointAnnotationKeyMap:
    x: str
    y: str
    z: str
    image_id: str


class ProcessingMode:
    RLN = PointAnnotationKeyMap(
        x="_rlnCoordinateX",
        y="_rlnCoordinateY",
        z="_rlnCoordinateZ",
        image_id="_rlnMicrographName",
    )

    @classmethod
    def _build_registry(cls):
        return {k.lower(): v for k, v in vars(cls).items() if not k.startswith("_")}

    @classmethod
    def get(cls, name: str) -> PointAnnotationKeyMap:
        return cls._build_registry()[name.lower()]

    @classmethod
    def all(cls) -> list[PointAnnotationKeyMap]:
        return list(cls._build_registry().values())
