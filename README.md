# semicalc

[![CI](https://github.com/YOUR-USERNAME/semicalc/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR-USERNAME/semicalc/actions)

A small, dependency-free **semiconductor physics calculator** for students and engineers.
Use it from the command line or import it as a Python library.

## What it calculates

| Command | Result |
|---|---|
| `intrinsic` | Band gap (Varshni model) and intrinsic carrier concentration `ni` vs temperature |
| `carriers` | Electron/hole concentration, n/p type and resistivity for a doped crystal |
| `pn` | p-n junction built-in potential and depletion width (with bias) |
| `diode` | Shockley diode current |
| `mosfet` | NMOS square-law drain current and operating region (cutoff / triode / saturation) |

Materials: Silicon (`si`), Germanium (`ge`), Gallium Arsenide (`gaas`).

## Install

```bash
git clone https://github.com/YOUR-USERNAME/semicalc.git
cd semicalc
pip install -e ".[dev]"
```

## Usage

```bash
semicalc intrinsic -m si -T 350
semicalc carriers --nd 1e16
semicalc pn --na 1e17 --nd 1e16 --bias 0.3
semicalc diode -v 0.65
semicalc mosfet --vgs 2 --vds 3 --vth 0.7
```

As a library:

```python
from semicalc import physics
from semicalc.materials import MATERIALS

si = MATERIALS["si"]
print(physics.built_in_potential(si, na=1e17, nd=1e16))   # volts
print(physics.resistivity(si, nd=1e16))                   # ohm*cm
```

## Key equations

- Thermal voltage: `Vt = kT/q`
- Band gap: `Eg(T) = Eg0 - aT² / (T + b)`
- Intrinsic carriers: `ni = sqrt(Nc·Nv) · exp(-Eg / 2kT)`
- Built-in potential: `Vbi = Vt · ln(Na·Nd / ni²)`
- Depletion width: `W = sqrt(2ε(Vbi − V)/q · (1/Na + 1/Nd))`
- Diode: `I = Is(exp(V/nVt) − 1)`
- MOSFET: `Id = ½k(Vgs−Vth)²` in saturation, `k[(Vgs−Vth)Vds − Vds²/2]` in triode

## Limitations

Educational models using textbook constants at ~300 K: full dopant ionisation, constant mobility, long-channel MOSFET (no short-channel effects). Not for production device design.

## Tests

```bash
pytest
```

## License

MIT
