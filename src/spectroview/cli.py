"""Command-line interface for spectroview."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from spectroview.io import open_cube


def _print_info(path: Path) -> int:
    cube = open_cube(path)
    wmin, wmax = cube.wavelength_range
    attrs = cube.attrs

    print(f"file: {path.resolve()}")
    print(f"dimensions: frame={cube.frame_count}, wavelength={len(cube.wavelength)}")
    print(f"wavelength range: {wmin:.4f} – {wmax:.4f} nm")
    print(f"frame count: {cube.frame_count}")
    print("attributes:")
    for key in sorted(attrs):
        print(f"  {key}: {attrs[key]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="spectroview",
        description="Viewer for SpectroCube netCDF datasets.",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Print file metadata and exit (no GUI).",
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        help="SpectroCube .nc file to open.",
    )
    args = parser.parse_args(argv)

    if args.info:
        if args.path is None:
            print("error: --info requires a file path", file=sys.stderr)
            return 1
        if not args.path.exists():
            print(f"error: file not found: {args.path}", file=sys.stderr)
            return 1
        return _print_info(args.path)

    if args.path is not None and not args.path.exists():
        print(f"error: file not found: {args.path}", file=sys.stderr)
        return 1

    from spectroview.gui.app import run_gui

    return run_gui(args.path)


if __name__ == "__main__":
    raise SystemExit(main())
