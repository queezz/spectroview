"""One-time script: produce a compact demo cube for bundling with spectroview.

Run from the repo root:
    python scripts/make_demo_cube.py

Output:
    src/spectroview/data/193777_demo.nc

Reduction strategy:
  - keep frames 0–19 (plasma frames; background frames are 36–49)
  - crop wavelength to 400–700 nm (covers Hδ, Hγ, BH, Hβ, Fulcher, Hα)
  - cast intensity to float32 (halves file size; sufficient for visualisation)
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import xarray as xr

SOURCE = Path(
    "../echelle_spectra/echelle_spectra/out/193777_spectrocube.nc"
)
DEST = Path("src/spectroview/data/193777_demo.nc")

N_FRAMES = 20       # keep first 20 plasma frames
WL_LO = 400.0       # nm  – covers Hδ at 409 nm with margin
WL_HI = 700.0       # nm  – covers Hα at 657.5 nm with margin


def main() -> None:
    src = SOURCE.resolve()
    if not src.exists():
        raise FileNotFoundError(f"Source cube not found: {src}")

    print(f"Reading  {src}")
    ds = xr.open_dataset(src)

    # --- temporal crop ---------------------------------------------------
    ds = ds.isel(frame=slice(0, N_FRAMES))

    # --- wavelength crop -------------------------------------------------
    wl = ds.wavelength.values
    mask = (wl >= WL_LO) & (wl <= WL_HI)
    ds = ds.sel(wavelength=ds.wavelength[mask])

    # --- cast to float32 to halve storage --------------------------------
    ds["intensity"] = ds["intensity"].astype(np.float32)

    # --- update attrs ----------------------------------------------------
    ds.attrs = {
        **ds.attrs,
        "demo": "true",
        "demo_note": (
            f"Reduced to {N_FRAMES} frames and {WL_LO}–{WL_HI} nm "
            "for package bundling; intensity cast to float32."
        ),
    }

    dest = DEST.resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Writing  {dest}")
    ds.to_netcdf(dest)

    size_mb = dest.stat().st_size / 1_048_576
    print(
        f"Done.  frames={ds.sizes['frame']}  "
        f"wavelength={ds.sizes['wavelength']}  "
        f"size={size_mb:.1f} MB"
    )


if __name__ == "__main__":
    main()
