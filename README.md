# Python ↔ Delphi Bridge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Delphi](https://img.shields.io/badge/Delphi-12%20VCL-red.svg)](https://www.embarcadero.com/products/delphi)
[![Python](https://img.shields.io/badge/Python-3.11%20embeddable-blue.svg)](https://www.python.org/downloads/windows/)
[![P4D](https://img.shields.io/badge/Python4Delphi-submodule-orange.svg)](https://github.com/pyscripter/python4delphi)

**Embed the Python data stack inside a Delphi VCL desktop app** — no separate Python install on the end-user machine.

This repository is a working starter that wires together:

- a **Delphi 12 VCL** host application
- **[Python4Delphi (P4D)](https://github.com/pyscripter/python4delphi)** for in-process Python
- the official **Python 3.11.9 embeddable** runtime (x64)
- a small **pandas** processing module that returns **JSON**

Delphi owns the UI and process lifetime. Python does the analytics. Communication is a simple, typed-enough contract: pass a path (or arguments), get JSON back.

---

## Table of contents

1. [Why this exists](#why-this-exists)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Repository layout](#repository-layout)
5. [Requirements](#requirements)
6. [Quick start](#quick-start)
7. [Embeddable Python setup (detailed)](#embeddable-python-setup-detailed)
8. [Delphi IDE configuration](#delphi-ide-configuration)
9. [Running the demo](#running-the-demo)
10. [How the bridge works](#how-the-bridge-works)
11. [Python API contract](#python-api-contract)
12. [Extending the project](#extending-the-project)
13. [Deployment notes](#deployment-notes)
14. [Submodule management](#submodule-management)
15. [Development workflow](#development-workflow)
16. [Troubleshooting](#troubleshooting)
17. [Security considerations](#security-considerations)
18. [Limitations](#limitations)
19. [Roadmap](#roadmap)
20. [License & credits](#license--credits)

---

## Why this exists

Delphi is excellent for native Windows desktop UIs. Python is excellent for pandas, NumPy, and scientific/ML workflows. Combining them in production usually forces one of these bad options:

| Approach | Problem |
| --- | --- |
| Install full Python on every PC | Fragile, version conflicts, IT friction |
| Shell out with `CreateProcess` | Process orchestration, path hell, poor UX |
| Rewrite analytics in Pascal | Slow, loses the Python ecosystem |

This template embeds CPython **in-process** via P4D and the official embeddable distribution. You keep a familiar Delphi EXE workflow and call Python like a library.

**Typical use cases**

- Point-cloud / CSV / tabular processing inside a desktop tool
- Prototyping data science logic in Python while shipping a VCL UI
- Reusing existing pandas pipelines from a Delphi host
- Shipping analytics without requiring a system-wide Python install

---

## Features

- **In-process Python** — loads `python311.dll` from a project-local embeddable runtime
- **No system Python required** on target machines (only the redistributables you ship)
- **Clean separation** — `app_delphi` (UI/host) vs `app_py` (processing)
- **JSON bridge** — Delphi calls `main(path)` and receives a JSON string
- **P4D + VarPyth** — natural `Import('main')` / method call style from Pascal
- **Git submodules** — Python4Delphi and embeddable Python versioned with the repo
- **Sample dataset** — XYZ point-cloud CSV to exercise the happy path
- **MIT licensed** application code (dependencies keep their own licenses)

---

## Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                     DelphiApp.exe (VCL)                     │
│                                                             │
│  MainForm                                                   │
│    └─ button click                                          │
│         └─ Import('main')  ──VarPyth──►  app_py/main.py     │
│         └─ main(path)      ◄── JSON ──┘                     │
│                                                             │
│  PyEngineService (singleton)                                │
│    • resolve project root from EXE path                     │
│    • DllName / PythonHome → embeddable Python folder        │
│    • SetDllDirectory                                        │
│    • LoadDll                                                │
│    • sys.path ← app_py                                      │
└───────────────────────────┬─────────────────────────────────┘
                            │ loads
                            ▼
            external_libraries/python-3.11.9-embed-amd64
            (python311.dll + site-packages: pandas, numpy)
```

**Request / response flow**

1. User clicks **Run Python Processing** (or you call the same code from your form).
2. Delphi reads an optional path from the memo (first line); otherwise uses `data/input/sample_points.txt`.
3. `PyEngine.EnsureReady` confirms the Python engine handle is valid.
4. `Import('main')` loads `app_py/main.py`.
5. `main(path)` runs pandas, builds a result `dict`, and returns `json.dumps(...)`.
6. Delphi displays the JSON string (or you parse it with `System.JSON`).

---

## Repository layout

```text
.
├── README.md
├── LICENSE                         # MIT
├── .gitignore
├── .gitmodules
│
├── app_delphi/                     # Delphi VCL host
│   ├── DelphiApp.dpr               # Program entry
│   ├── DelphiApp.dproj             # IDE project
│   ├── DelphiApp.res
│   ├── forms/
│   │   ├── MainForm.pas            # Demo UI + Python call
│   │   └── MainForm.dfm
│   └── services/
│       └── PyEngineService.pas     # Embeddable Python bootstrap
│
├── app_py/                         # Python processing side
│   ├── main.py                     # Entry point called from Delphi
│   └── requirements.txt            # Packages for the embeddable runtime
│
├── data/
│   └── input/
│       └── sample_points.txt       # Sample XYZ CSV (header: x,y,z)
│
└── external_libraries/             # Git submodules (not vendored as copies)
    ├── python4delphi/              # https://github.com/pyscripter/python4delphi
    └── python-3.11.9-embed-amd64/  # Embeddable CPython 3.11.9 (x64)
```

Build outputs (`Win64/`, `__history/`, `.dcu`, etc.) are gitignored and must not be committed.

---

## Requirements

| Component | Notes |
| --- | --- |
| **OS** | Windows x64 |
| **Delphi** | 12 recommended (Community or higher), VCL |
| **Platform** | **Win64** (matches the embeddable amd64 runtime) |
| **Git** | Required for submodules |
| **VC++ Redistributable** | Needed on machines that run the embeddable CPython build |
| **Disk** | Room for submodules + pip packages inside the embeddable tree |

This project targets **Win64 only** with the provided amd64 embeddable Python. Win32 would need a matching 32-bit runtime and project changes.

---

## Quick start

### 1. Clone with submodules

```bash
git clone --recurse-submodules https://github.com/juandapradam12/PythonDelphiPOC.git
cd PythonDelphiPOC
```

If you cloned without submodules:

```bash
git submodule update --init --recursive
```

Verify:

```bash
git submodule status
dir external_libraries\python-3.11.9-embed-amd64\python311.dll
dir external_libraries\python4delphi\Source
```

### 2. Prepare embeddable Python + install deps

See [Embeddable Python setup (detailed)](#embeddable-python-setup-detailed). Short version (after pip works):

```bat
cd external_libraries\python-3.11.9-embed-amd64
python.exe -m pip install -r ..\..\app_py\requirements.txt
```

### 3. Configure Delphi and run

1. Open `app_delphi\DelphiApp.dproj`.
2. Set platform to **Win64**.
3. Add P4D library paths (see [Delphi IDE configuration](#delphi-ide-configuration)).
4. Build + Run.
5. Click **Run Python Processing**.

### 4. Optional: smoke-test Python without Delphi

```bat
external_libraries\python-3.11.9-embed-amd64\python.exe app_py\main.py data\input\sample_points.txt
```

---

## Embeddable Python setup (detailed)

The official Windows [embeddable package](https://docs.python.org/3/using/windows.html#the-embeddable-package) is intentionally minimal. Out of the box it often **cannot** `import pip` or third-party packages until you enable `site` and install pip once.

### Enable `site` packages

In `external_libraries\python-3.11.9-embed-amd64\python311._pth` (filename may vary slightly by build), ensure `import site` is **uncommented**, for example:

```text
python311.zip
.
import site
```

Without this, packages installed under `Lib\site-packages` may be invisible.

### Bootstrap pip (once)

If `python.exe -m pip` fails:

1. Download [`get-pip.py`](https://bootstrap.pypa.io/get-pip.py).
2. Run it with the **embeddable** interpreter:

```bat
cd external_libraries\python-3.11.9-embed-amd64
python.exe get-pip.py
```

### Install project dependencies

```bat
cd external_libraries\python-3.11.9-embed-amd64
python.exe -m pip install -r ..\..\app_py\requirements.txt
python.exe -m pip show pandas numpy
```

Current `app_py/requirements.txt`:

```text
numpy>=1.26
pandas>=2.1
```

**Important:** always install into this embeddable interpreter. Packages on a system/global Python will not be seen by the Delphi-hosted runtime.

### Verify imports

```bat
python.exe -c "import pandas, numpy; print(pandas.__version__, numpy.__version__)"
```

---

## Delphi IDE configuration

1. Open `app_delphi\DelphiApp.dproj` in the Delphi IDE.
2. **Project → Options → Delphi Compiler → Target platform:** `Windows 64-bit`.
3. Add to **Library path** (and Search path if you prefer):

   - `$(PROJECTDIR)\..\external_libraries\python4delphi\Source`
   - `$(PROJECTDIR)\..\external_libraries\python4delphi\Source\vcl`

   Absolute paths also work if relative macros are awkward in your IDE version.

4. Confirm these units resolve: `PythonEngine`, `VarPyth`.
5. Build (**Project → Build DelphiApp**).

`PyEngineService` is created in the unit `initialization` section, so Python is bootstrapped when the app starts (not only on button click).

---

## Running the demo

### From the VCL UI

1. Start `DelphiApp`.
2. You should see `App initialized` in the memo.
3. Optionally type a file path on the **first line** of the memo.
4. Click **Run Python Processing**.
5. JSON output is appended below.

If the first memo line is empty, the default path is:

```text
data/input/sample_points.txt
```

That path is resolved from the **repository root** on the Python side (see API section).

### Expected sample output

```json
{
  "status": "ok",
  "path": "C:\\...\\data\\input\\sample_points.txt",
  "rows": 97,
  "cols": 3,
  "columns": ["x", "y", "z"],
  "first_row": {
    "x": 381.3919131502,
    "y": 430.2502623372,
    "z": 109.0358264945
  }
}
```

### EXE location and project root

`PyEngineService.ProjectRootFromExe` assumes the usual Delphi output layout:

```text
<repo>/app_delphi/Win64/Debug/DelphiApp.exe
         ^         ^     ^
         +3 parents = <repo>
```

If you change output directories, update that helper or Python will fail to find `python311.dll` / `app_py`.

---

## How the bridge works

### Delphi: `PyEngineService`

Responsibilities:

| Step | What it does |
| --- | --- |
| Resolve root | Walk up from EXE dir to repo root |
| Locate runtime | `external_libraries\python-3.11.9-embed-amd64\python311.dll` |
| Configure engine | `UseLastKnownVersion := False`, set `DllName` + `PythonHome` |
| Help Windows | `SetDllDirectory` on the embeddable folder |
| Load | `FPython.LoadDll` |
| Import path | Insert `app_py` into `sys.path` |

Key idea: **never rely on a machine-wide Python**. The DLL path is always project-local.

### Delphi: `MainForm`

Minimal UI that demonstrates the call pattern:

```pascal
PyEngine.EnsureReady;
PyMain := Import('main');       // app_py/main.py
PyRes  := PyMain.main(PathStr); // must return something VarPyth can convert
Memo1.Lines.Add(VarToStr(PyRes));
```

Errors from Python or missing files are caught and shown in the memo.

### Python: `app_py/main.py`

| Function | Role |
| --- | --- |
| `process_file(path)` | Load CSV/TXT with pandas, return a summary `dict` |
| `main(path=None)` | Delphi entry point; always returns a **JSON string** |
| `__main__` | CLI helper for standalone testing |

Relative paths are joined to the repository root (`parent` of `app_py`).

---

## Python API contract

### `main(path: str | None) -> str`

Always returns a JSON string.

#### Success — file processed

```json
{
  "status": "ok",
  "path": "<absolute path>",
  "rows": 97,
  "cols": 3,
  "columns": ["x", "y", "z"],
  "first_row": { "x": 0.0, "y": 0.0, "z": 0.0 }
}
```

#### Success — no path (hello / connectivity check)

```json
{
  "status": "ok",
  "message": "Hello from Python! Session=<uuid>, Time=<iso8601>"
}
```

#### Error

```json
{
  "status": "error",
  "message": "File not found: ..."
}
```

or

```json
{
  "status": "error",
  "message": "Error reading file ...: <ExceptionType>: <details>"
}
```

### Design rules (recommended)

1. **Keep `main` stable** — Delphi should call one or a few well-known entry points.
2. **Return JSON strings** for structured results (easy to log, display, and parse).
3. **Put failures in JSON** when possible; reserve Delphi exceptions for engine/bootstrap failures.
4. **Avoid GUI / blocking work** on the Python side unless you add threading consciously (VCL is single-threaded by default).

---

## Extending the project

### Add more Python logic

1. Create modules under `app_py/` (e.g. `app_py/pipeline.py`).
2. Import them from `main.py` or via `Import('pipeline')` from Delphi.
3. Pin new packages in `requirements.txt` and reinstall into the **embeddable** runtime.
4. Keep heavy logic in Python; keep UI and file-picker UX in Delphi.

Example Delphi call to another module:

```pascal
PyPipe := Import('pipeline');
PyRes  := PyPipe.run_analysis(PathStr, OptionsJson);
```

### Parse JSON in Delphi

Instead of only showing text:

```pascal
uses System.JSON;

// ...
var
  Doc: TJSONValue;
begin
  Doc := TJSONObject.ParseJSONValue(VarToStr(PyRes));
  try
    // read fields...
  finally
    Doc.Free;
  end;
end;
```

### Change the default dataset

- Replace `data/input/sample_points.txt`, or
- Change the default string in `MainForm.BtnRunClick`.

### Support other Python versions

You would need to:

1. Swap the embeddable submodule / folder
2. Update DLL name (`python3xx.dll`) in `PyEngineService`
3. Rebuild and retest P4D against that version

Stick to 3.11.x unless you have a reason to move.

---

## Deployment notes

To run on a machine **without** Delphi or a system Python, ship at least:

```text
YourApp.exe
external_libraries/python-3.11.9-embed-amd64/   # full tree, including site-packages
app_py/                                         # your .py modules
data/                                           # if required at runtime
```

Also ensure:

- Folder layout still matches what `ProjectRootFromExe` expects, **or** you change that function for an installer layout
- Visual C++ Redistributable is installed
- You tested on a clean Windows VM

**Do not** assume `pip` is available on the customer machine; bake dependencies into the embeddable tree before shipping.

---

## Submodule management

Configured in `.gitmodules`:

| Path | Upstream |
| --- | --- |
| `external_libraries/python4delphi` | `https://github.com/pyscripter/python4delphi.git` |
| `external_libraries/python-3.11.9-embed-amd64` | `https://github.com/juandapradam12/PythonEmbeddable-3.11.9.git` |

### Initialize / update after clone or pull

```bash
git submodule update --init --recursive
```

### Update P4D to latest remote commit

```bash
git submodule update --remote external_libraries/python4delphi
git add external_libraries/python4delphi
git commit -m "chore: update Python4Delphi submodule"
```

Always rebuild the Delphi project after updating P4D.

---

## Development workflow

### Daily loop

1. Edit Python in `app_py/` — fast to test via CLI.
2. Edit Delphi host / UI as needed.
3. Run the VCL app for integration tests.
4. Commit source only (never `Win64/`, `__history/`, `.dcu`, `.exe`).

### Standalone Python test

```bat
external_libraries\python-3.11.9-embed-amd64\python.exe app_py\main.py data\input\sample_points.txt
```

### Suggested commit hygiene

- Keep commits focused (Python logic vs Delphi host vs docs)
- Prefer conventional prefixes when useful: `feat:`, `fix:`, `docs:`, `chore:`
- Re-test the button path after any change to `PyEngineService` or submodule paths

---

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `Python DLL not found at: ...` | Submodule missing or wrong EXE layout | `git submodule update --init --recursive`; confirm EXE under `app_delphi\Win64\...` |
| `ImportError: No module named pandas` | Deps installed on system Python, or `import site` disabled | Install into embeddable runtime; uncomment `import site` in `python311._pth` |
| `pip` not found on embeddable Python | Minimal embeddable layout | Bootstrap with `get-pip.py` |
| Cannot compile `PythonEngine` / `VarPyth` | Library path incomplete | Add P4D `Source` and `Source\vcl` |
| App starts then dies on Python init | Bad DLL / wrong bitness / missing VC++ runtime | Confirm Win64 + amd64 DLL; install VC++ Redistributable |
| File not found from Python | Relative path / root resolution | Use repo-relative paths like `data/input/...` or pass absolute paths |
| Works in IDE, fails when installed elsewhere | Deployed folder layout differs | Adjust `ProjectRootFromExe` or ship a fixed `PythonHome` |
| VS Code / Explorer shows “dirty” submodule | Submodule checked out at different commit | Normal — commit intentional submodule bumps only |

### Debugging tips

1. Run `main.py` from the CLI first to isolate Python issues.
2. Log `DllPath`, `PythonHome`, and resolved project root from Delphi if bootstrap fails.
3. Confirm `python311.dll` architecture matches the Delphi target (both x64).

---

## Security considerations

This bridge executes Python **inside your process**. Treat it with the same care as loading a native plugin:

- **Do not** run untrusted `.py` files or user-supplied scripts without a sandbox strategy.
- Validate/sanitize file paths coming from the UI.
- Prefer returning structured JSON over executing dynamic code strings from Delphi.
- Keep the embeddable runtime and pip packages updated for CVE fixes.
- Avoid logging secrets; this sample has no credentials, and `.env` files are gitignored.

---

## Limitations

Be aware of what this starter does **not** include yet:

- No automated test suite / CI
- No FMX / cross-platform host (VCL + Win64 only)
- No background thread marshaling helpers for long Python jobs
- No installer project (Inno Setup / MSIX / etc.)
- Sample processing is a CSV summary — not a full domain pipeline
- Embeddable pip bootstrap still requires a one-time manual setup on new machines/clones

These are intentional scope boundaries so the core bridge stays clear and copyable.

---

## Roadmap

Ideas for future iterations:

- [ ] Longer-running jobs with cancel + UI thread marshaling
- [ ] Richer sample pipelines (filtering, transforms, exports)
- [ ] Delphi-side JSON helpers for common result shapes
- [ ] Optional installer / portable zip layout docs
- [ ] Basic pytest coverage for `app_py`
- [ ] CI that at least lint/tests the Python side

Contributions and issue reports are welcome if you fork or adapt this for your stack.

---

## License & credits

### This repository

Application code in this repository is released under the **MIT License** — see [LICENSE](LICENSE).

### Third-party components

| Component | Role | License |
| --- | --- | --- |
| [Python4Delphi](https://github.com/pyscripter/python4delphi) | Delphi ↔ Python integration | See upstream repo |
| [CPython](https://www.python.org/) embeddable | Runtime | [PSF License](https://docs.python.org/3/license.html) |
| [pandas](https://pandas.pydata.org/) / [NumPy](https://numpy.org/) | Sample processing stack | Their respective licenses |

### Related links

- [Python4Delphi documentation & demos](https://github.com/pyscripter/python4delphi)
- [Python embeddable package notes](https://docs.python.org/3/using/windows.html#the-embeddable-package)
- [Embarcadero Delphi](https://www.embarcadero.com/products/delphi)

---

**Keep Delphi for the product UI. Keep Python for the data. Let this bridge glue them without fighting installers.**
