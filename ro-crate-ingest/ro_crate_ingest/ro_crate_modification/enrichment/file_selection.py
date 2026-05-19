from typing import Any

from ro_crate_ingest.ro_crate_modification.enrichment.utils import match_patterns


def selection_patterns(selection: Any) -> list[str]:
    patterns = getattr(selection, "patterns", None)
    if patterns is not None:
        return list(patterns)
    return []


def selection_paths(selection: Any) -> list[str]:
    paths = getattr(selection, "paths", None)
    if paths is not None:
        return list(paths)
    return []


def match_selection(file_path: str, selection: Any) -> bool:
    return file_path in selection_paths(selection) or match_patterns(
        file_path, selection_patterns(selection)
    )


def flatten_selections(selections: list[Any]) -> list[Any]:
    return [
        selection
        for selection in selections
        if selection_paths(selection) or selection_patterns(selection)
    ]
