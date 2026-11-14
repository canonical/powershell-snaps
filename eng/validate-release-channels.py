#!/usr/bin/env python3
"""Check that each channel workflow passes its channel to reusable jobs."""

from pathlib import Path
import re
import sys


CHANNELS = ("lts", "preview", "stable")
REUSABLE_JOBS = ("needs-store-publishing", "build", "test", "publish")
RELEASE = re.compile(r"(?m)^      release:\s*(.+?)\s*$")
JOB = re.compile(r"(?m)^  ([\w-]+):\s*$")


def validate(workflows_dir: Path) -> list[str]:
    errors = []
    for channel in CHANNELS:
        path = workflows_dir / f"powershell-{channel}.yaml"
        contents = path.read_text()
        jobs = JOB.split(contents.split("\njobs:\n", 1)[1])
        blocks = dict(zip(jobs[1::2], jobs[2::2]))

        for job in REUSABLE_JOBS:
            values = RELEASE.findall(blocks.get(job, ""))
            if len(values) != 1 or values[0].strip("'\"") != channel:
                errors.append(f"{path}: {job} must set release to {channel!r}")
    return errors


if __name__ == "__main__":
    workflow_dir = Path(__file__).resolve().parents[1] / ".github/workflows"
    problems = validate(workflow_dir)
    for problem in problems:
        print(problem, file=sys.stderr)
    sys.exit(bool(problems))
