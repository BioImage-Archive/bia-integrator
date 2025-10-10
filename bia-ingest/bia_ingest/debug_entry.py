import os
import debugpy
from bia_ingest.cli import app


def main() -> None:
    if os.environ.get("DEBUGPY_LISTEN") != "1":
        debugpy.listen(("127.0.0.1", 5678))
        os.environ["DEBUGPY_LISTEN"] = "1"
    debugpy.wait_for_client()
    app()
