"""Python entry point called from the Delphi host.

Delphi imports this module and calls main(path). The return value is always a
JSON string so the VCL side can display or parse it without custom marshalling.
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime

import pandas as pd


def process_file(path: str) -> dict:
    """Load a CSV/TXT file into a DataFrame and return a compact summary."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.isabs(path):
        path = os.path.normpath(os.path.join(base_dir, path))

    if not os.path.exists(path):
        return {"status": "error", "message": f"File not found: {path}"}

    try:
        df = pd.read_csv(path, sep=None, engine="python", on_bad_lines="skip")
        rows, cols = df.shape
        return {
            "status": "ok",
            "path": path,
            "rows": rows,
            "cols": cols,
            "columns": [str(c) for c in df.columns],
            "first_row": df.iloc[0].to_dict() if rows > 0 else {},
        }
    except Exception as exc:  # noqa: BLE001 - surface any read failure to Delphi
        return {
            "status": "error",
            "message": f"Error reading file {path}: {type(exc).__name__}: {exc}",
        }


def main(path: str | None = None) -> str:
    """Entry point for Delphi. Returns pretty-printed JSON."""
    if path:
        result = process_file(path)
    else:
        result = {
            "status": "ok",
            "message": (
                f"Hello from Python! Session={uuid.uuid4()}, "
                f"Time={datetime.now().isoformat()}"
            ),
        }
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(main(sys.argv[-1]))
    else:
        print("Usage: python main.py <path-to-file>")
