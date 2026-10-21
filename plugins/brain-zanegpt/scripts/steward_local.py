#!/usr/bin/env python3
"""Run the memory repo's own steward against the plugin's merged view.

Usage: steward_local.py <view>/memory/scripts/steward.py

The steward, its checks and its cited_by/validate follow-ups run unmodified,
with one exception: a promoted lesson files into `<owner>__<repo>__local.md`
instead of the shared project file. Shared files can gain new entries in a
later snapshot, so a local lesson numbered into one would collide with an
upstream E-id after an upgrade.
"""

from __future__ import annotations

import importlib.util
import os
import sys

LOCAL_SUFFIX = "__local"


def main() -> int:
    path = os.path.abspath(sys.argv[1])
    os.environ["BRAIN_STEWARD_ROOT"] = os.path.dirname(os.path.dirname(path))
    sys.argv = [path]
    spec = importlib.util.spec_from_file_location("brain_steward", path)
    steward = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(steward)
    shared_project_file = steward.project_file

    def project_file(fields):
        rel = shared_project_file(fields)
        if not rel or rel[:-3].endswith(LOCAL_SUFFIX):
            return rel
        return rel[:-3] + LOCAL_SUFFIX + ".md"

    steward.project_file = project_file
    return steward.main()


if __name__ == "__main__":
    sys.exit(main())
