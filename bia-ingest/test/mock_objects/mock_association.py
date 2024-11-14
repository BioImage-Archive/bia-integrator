"""Return associations in study components"""

from typing import List, Dict


def get_association_dicts() -> Dict[str, List[Dict]]:
    """Return list of List[dict]s for study component associaions

    Created independently to prevent recursion when computing
    datasets as they contain uuids of specimens and specimens
    are generated looking at associations in dataset
    """

    return {
        # Associations for study component (dataset) 1
        "Study Component 1": [
            {
                "image_analysis": "Test image analysis",
                "image_correlation": None,
                "biosample": "Test Biosample 1",
                "image_acquisition": "Test Primary Screen Image Acquisition",
                "specimen": "Test specimen 1",
            },
            {
                "image_analysis": "Test image analysis",
                "image_correlation": None,
                "biosample": "Test Biosample 2 ",
                "image_acquisition": "Test Secondary Screen Image Acquisition",
                "specimen": "Test specimen 1",
            },
        ],
        # Associations for study component (dataset) 2
        "Study Component 2": [
            {
                "image_analysis": "Test image analysis",
                "image_correlation": None,
                "biosample": "Test Biosample 2 ",
                "image_acquisition": "Test Primary Screen Image Acquisition",
                "specimen": "Test specimen 2",
            },
        ],
    }
