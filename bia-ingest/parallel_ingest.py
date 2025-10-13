"""
Parallel ingest of BioStudies accession IDs.

This script takes a JSON file containing a list of BioStudies accession IDs,
runs each accession ID in parallel using the `run_one` function, and writes
the output to two files: one for successes and one for failures.

Usage:
    poetry run python parallel_ingest.py --json <accessions.json> --workers <num workers>

Arguments:
    --json: Path to the JSON file containing the list of accessions.
    --workers: Number of workers to use for parallel processing.

Example:
    poetry run python parallel_ingest.py  --jobs 10

When not specified, the default number of workers is the number of CPU cores and
the output files will be named `ingest_success.log` and `ingest_failure.log`.

File input example:

    [
        "S-BIAD590",
        "S-BIAD590",
        "S-BIAD590",
        "S-BIAD590",
        "S-BIAD590",
        "S-BIAD590",
        "S-BIAD590",
        "S-BIAD590",
        "S-BIAD590",
        "S-BIAD590",
        ...
    ]
"""

#!/usr/bin/env python3
import argparse
import asyncio
import json
import os
from tqdm import tqdm

BASE_CMD = [
    "poetry",
    "run",
    "biaingest",
    "ingest",
    "--dryrun",
    "-om=simple",
    "--process-filelist=skip",
]
# Each accession is appended as final argument.


async def run_one(accession: str) -> tuple[str, bytes]:
    cmd = BASE_CMD + [str(accession)]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    out, _ = await proc.communicate()
    return accession, out or b""


async def bounded_run(accession: str, sem: asyncio.Semaphore) -> tuple[str, bytes]:
    async with sem:
        return await run_one(accession)


async def amain(args):
    with open(args.json, "r", encoding="utf-8") as f:
        accessions = json.load(f)
    if not isinstance(accessions, list):
        raise SystemExit("accessions.json must contain a JSON list")

    sem = asyncio.Semaphore(args.jobs)
    tasks = [asyncio.create_task(bounded_run(acc, sem)) for acc in accessions]

    success_file = "ingest_success.log"
    failure_file = "ingest_failure.log"

    with (
        open(success_file, "wb") as success_out,
        open(failure_file, "wb") as failure_out,
        tqdm(total=len(tasks), desc="ingest", unit="job") as bar,
    ):
        for coro in asyncio.as_completed(tasks):
            try:
                _, data = await coro
            except Exception:
                _, data = "", b""
            if data:
                if b"success" in data.lower():
                    success_out.write(data)
                else:
                    failure_out.write(data)
            bar.update(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="accessions.json")
    ap.add_argument("--jobs", "-j", type=int, default=os.cpu_count() or 4)
    args = ap.parse_args()
    asyncio.run(amain(args))


if __name__ == "__main__":
    main()
