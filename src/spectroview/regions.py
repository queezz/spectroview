"""Built-in wavelength regions for quick zoom."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WavelengthRegion:
    name: str
    lo_nm: float
    hi_nm: float

    def overlaps(self, wmin: float, wmax: float) -> bool:
        return self.hi_nm >= wmin and self.lo_nm <= wmax


BUILTIN_REGIONS: tuple[WavelengthRegion, ...] = (
    WavelengthRegion("BH Q-branch", 432.8, 434.2),
    WavelengthRegion("H-gamma", 433.5, 434.8),
    WavelengthRegion("H-beta", 485.0, 487.5),
    WavelengthRegion("H-alpha", 655.5, 657.5),
    WavelengthRegion("Fulcher", 590.0, 650.0),
)


def available_regions(wmin: float, wmax: float) -> list[WavelengthRegion]:
    """Return built-in regions that overlap the cube wavelength range."""
    return [r for r in BUILTIN_REGIONS if r.overlaps(wmin, wmax)]
