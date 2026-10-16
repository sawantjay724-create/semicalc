"""Command-line interface: semicalc <command> [options]."""
from __future__ import annotations

import argparse
import sys

from . import __version__, physics as ph
from .materials import MATERIALS, get_material


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("-m", "--material", default="si", choices=list(MATERIALS), help="default: si")
    p.add_argument("-T", "--temp", type=float, default=300.0, help="temperature in kelvin (default 300)")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="semicalc", description="Semiconductor physics calculator.")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("intrinsic", help="band gap and intrinsic carrier concentration")
    _common(s)

    s = sub.add_parser("carriers", help="electron/hole concentration and resistivity of doped material")
    _common(s)
    s.add_argument("--nd", type=float, default=0.0, help="donor doping, cm^-3")
    s.add_argument("--na", type=float, default=0.0, help="acceptor doping, cm^-3")

    s = sub.add_parser("pn", help="p-n junction built-in potential and depletion width")
    _common(s)
    s.add_argument("--na", type=float, required=True, help="p-side acceptors, cm^-3")
    s.add_argument("--nd", type=float, required=True, help="n-side donors, cm^-3")
    s.add_argument("--bias", type=float, default=0.0, help="applied voltage (+ forward), default 0")

    s = sub.add_parser("diode", help="Shockley diode current")
    s.add_argument("-v", "--voltage", type=float, required=True)
    s.add_argument("--is", dest="i_s", type=float, default=1e-12, help="saturation current, A")
    s.add_argument("-n", "--ideality", type=float, default=1.0)
    s.add_argument("-T", "--temp", type=float, default=300.0)

    s = sub.add_parser("mosfet", help="NMOS square-law drain current")
    s.add_argument("--vgs", type=float, required=True)
    s.add_argument("--vds", type=float, required=True)
    s.add_argument("--vth", type=float, default=0.7, help="threshold voltage (default 0.7)")
    s.add_argument("-k", type=float, default=2e-4, help="mu*Cox*W/L in A/V^2 (default 2e-4)")
    return p


def run(args: argparse.Namespace) -> list[str]:
    if args.cmd == "diode":
        i = ph.diode_current(args.voltage, args.i_s, args.ideality, args.temp)
        return [f"Diode current: {i:.4e} A"]
    if args.cmd == "mosfet":
        i, region = ph.mosfet_current(args.vgs, args.vds, args.vth, args.k)
        return [f"Region: {region}", f"Drain current: {i:.4e} A"]

    mat = get_material(args.material)
    t = args.temp
    out = [f"Material: {mat.name} at {t:g} K"]
    if args.cmd == "intrinsic":
        out += [f"Thermal voltage: {ph.thermal_voltage(t):.4f} V",
                f"Band gap: {ph.band_gap(mat, t):.4f} eV",
                f"Intrinsic carriers ni: {ph.intrinsic_carriers(mat, t):.3e} cm^-3"]
    elif args.cmd == "carriers":
        n, p = ph.carrier_concentrations(mat, args.nd, args.na, t)
        kind = "n-type" if n > p else "p-type"
        out += [f"Type: {kind}", f"Electrons n: {n:.3e} cm^-3", f"Holes p: {p:.3e} cm^-3",
                f"Resistivity: {ph.resistivity(mat, args.nd, args.na, t):.4e} ohm*cm"]
    elif args.cmd == "pn":
        vbi = ph.built_in_potential(mat, args.na, args.nd, t)
        w = ph.depletion_width(mat, args.na, args.nd, args.bias, t)
        out += [f"Built-in potential Vbi: {vbi:.4f} V",
                f"Depletion width at {args.bias:g} V: {w * 1e4:.4f} um"]
    return out


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        print("\n".join(run(args)))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
