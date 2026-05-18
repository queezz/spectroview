# spectroview

Lightweight viewer and plotting tools for [SpectroCube](https://github.com/queezz/spectrocube) datasets.

## Role in the stack

| Repository | Role |
|------------|------|
| **spectrocube** | Data standard — xarray/netCDF calibrated spectral cubes |
| **echelle_spectra** | Producer pipeline — converts echelle data into SpectroCube files |
| **spectroview** (this repo) | Consumer — read-only viewing and plotting; no calibration or fitting |

## Usage

Print metadata:

```bash
spectroview --info path/to/file_spectrocube.nc
```

Open the GUI:

```bash
spectroview path/to/file_spectrocube.nc
```

The GUI shows cube metadata, a frame slider, a spectrum plot (pyqtgraph), and a region selector to zoom known wavelength bands (Balmer lines, Fulcher, etc.).

### Python API

```python
from spectroview import open_cube
from spectroview.plotting import plot_spectrum, plot_region, plot_map

cube = open_cube("193777_spectrocube.nc")
wl, y = cube.spectrum(frame=0)
plot_spectrum(cube, frame=0)
plot_region(cube, "H-alpha", frame=0)
plot_map(cube)
```

## Tests

```bash
pytest
```

Core tests do not require Qt.

## Virtual environment

Use `~/.venvs/spectroview` (or `%USERPROFILE%\.venvs\spectroview` on Windows). Do not use system Python or conda.

**macOS / Linux**

```bash
python3 -m venv ~/.venvs/spectroview
source ~/.venvs/spectroview/bin/activate
pip install -e ".[dev]"
pip install -e ../2026-spectrocube
pip install -e ../echelle_spectra
```

**Windows (PowerShell)**

```powershell
python -m venv $env:USERPROFILE\.venvs\spectroview
& $env:USERPROFILE\.venvs\spectroview\Scripts\Activate.ps1
pip install -e ".[dev]"
pip install -e ..\2026-spectrocube
pip install -e ..\echelle_spectra
```

Point the editor at `~/.venvs/spectroview/bin/python` (see `.vscode/settings.json`).

## License

MIT
