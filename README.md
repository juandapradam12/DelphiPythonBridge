# Python ↔ Delphi Bridge

Embed the **Python data stack** inside a **Delphi VCL** desktop app — no separate Python install on the end-user machine.

This repo is a working starter for [Python4Delphi (P4D)](https://github.com/pyscripter/python4delphi) + the official **Python 3.11 embeddable** runtime. Delphi owns the UI and process lifetime; Python does the number-crunching and returns **JSON**.

## Why this exists

Delphi is great for Windows desktop UIs. Python is great for pandas, NumPy, and ML. Shipping both usually means:

- installing a full Python on every PC, or
- bolting on fragile `CreateProcess` scripts, or
- rewriting analytics in Pascal

This template embeds Python **in-process**, so you keep one EXE workflow and call Python like a library.

## What you get

| Piece | Role |
| --- | --- |
| `app_delphi/` | VCL host that loads `python311.dll` and calls into Python |
| `app_py/main.py` | Processing entry point; returns JSON Delphi can show or parse |
| `external_libraries/python4delphi` | P4D submodule |
| `external_libraries/python-3.11.9-embed-amd64` | Embeddable CPython 3.11.9 submodule |
| `data/input/sample_points.txt` | Sample XYZ point-cloud CSV used by the demo |

**Flow:** Delphi button → `Import('main')` → `main(path)` → JSON string → memo / your parser.

## Quick start

### 1. Clone with submodules

```bash
git clone --recurse-submodules https://github.com/juandapradam12/PythonDelphiPOC.git
cd PythonDelphiPOC
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive
```

### 2. Install Python packages into the embeddable runtime

From a Windows machine (PowerShell or cmd):

```bat
cd external_libraries\python-3.11.9-embed-amd64
python.exe -m pip install -r ..\..\app_py\requirements.txt
```

> Tip: embeddable Python often needs `python311._pth` adjusted (uncomment `import site`) and `get-pip.py` once before `pip` works. See the [official embeddable docs](https://docs.python.org/3/using/windows.html#the-embeddable-package).

### 3. Open and run the Delphi project

1. Open `app_delphi\DelphiApp.dproj` in Delphi 12 (Community or higher).
2. Set platform to **Win64**.
3. Add to **Library path**:
   - `external_libraries\python4delphi\Source`
   - `external_libraries\python4delphi\Source\vcl`
4. Build and run.
5. Click **Run Python Processing** (leave the memo empty to use `data/input/sample_points.txt`).

### 4. Optional: test Python alone

```bat
external_libraries\python-3.11.9-embed-amd64\python.exe app_py\main.py data\input\sample_points.txt
```

Example response:

```json
{
  "status": "ok",
  "path": "...\\data\\input\\sample_points.txt",
  "rows": 97,
  "cols": 3,
  "columns": ["x", "y", "z"],
  "first_row": {"x": 381.39, "y": 430.25, "z": 109.04}
}
```

## Project layout

```text
├── app_delphi/                 # Delphi VCL host
│   ├── DelphiApp.dpr
│   ├── forms/MainForm.*        # Demo UI
│   └── services/PyEngineService.pas   # Loads embeddable Python + sys.path
├── app_py/
│   ├── main.py                 # Called from Delphi
│   └── requirements.txt
├── data/input/                 # Sample datasets
├── external_libraries/         # Git submodules (P4D + embeddable Python)
├── LICENSE
└── README.md
```

## Extending the bridge

1. Add functions in `app_py/` (keep a stable `main(...)` or import named modules from Delphi).
2. Return JSON (or primitives P4D already maps).
3. On the Delphi side, call via `VarPyth`:

```pascal
PyMain := Import('main');
PyRes  := PyMain.main(PathStr);
Memo1.Lines.Add(VarToStr(PyRes));
```

`PyEngineService` resolves the project root from the EXE path (`app_delphi\Win64\Debug\...`), points `DllName` / `PythonHome` at the embeddable folder, and inserts `app_py` into `sys.path`.

## Requirements

- Windows x64
- Delphi 12 (tested) with VCL
- Git (for submodules)
- Visual C++ Redistributable on target machines (usual for embeddable CPython)

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `Python DLL not found` | Confirm submodule `external_libraries/python-3.11.9-embed-amd64` is checked out and contains `python311.dll` |
| `ImportError` / missing pandas | Install deps into the **embeddable** interpreter, not system Python |
| Delphi compile errors on `PythonEngine` | Add P4D `Source` (+ `Source\vcl`) to the library path; Win64 platform |
| Wrong file paths at runtime | Run from a build under `app_delphi\Win64\...` so `ProjectRootFromExe` walks up to the repo root |

## License

MIT — see [LICENSE](LICENSE).

Python4Delphi and CPython remain under their own licenses.
