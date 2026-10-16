import math

import pytest

from semicalc import physics as ph
from semicalc.cli import main
from semicalc.materials import MATERIALS, get_material

SI = MATERIALS["si"]


def test_thermal_voltage_room_temp():
    assert ph.thermal_voltage(300) == pytest.approx(0.02585, abs=1e-4)


def test_silicon_band_gap_300k():
    assert ph.band_gap(SI, 300) == pytest.approx(1.12, abs=0.02)


def test_band_gap_shrinks_with_temperature():
    assert ph.band_gap(SI, 400) < ph.band_gap(SI, 300)


def test_intrinsic_carriers_order_of_magnitude():
    assert 1e9 < ph.intrinsic_carriers(SI, 300) < 3e10


def test_intrinsic_grows_with_temperature():
    assert ph.intrinsic_carriers(SI, 400) > ph.intrinsic_carriers(SI, 300) * 100


def test_n_type_doping():
    n, p = ph.carrier_concentrations(SI, nd=1e16)
    assert n == pytest.approx(1e16, rel=1e-3)
    assert n * p == pytest.approx(ph.intrinsic_carriers(SI) ** 2, rel=1e-6)


def test_p_type_doping():
    n, p = ph.carrier_concentrations(SI, na=1e16)
    assert p > n and p == pytest.approx(1e16, rel=1e-3)


def test_resistivity_drops_with_doping():
    assert ph.resistivity(SI, nd=1e17) < ph.resistivity(SI, nd=1e15)


def test_resistivity_1e16_n_si_about_half_ohm_cm():
    assert ph.resistivity(SI, nd=1e16) == pytest.approx(0.46, rel=0.1)


def test_built_in_potential_typical_si():
    assert ph.built_in_potential(SI, 1e17, 1e17) == pytest.approx(0.83, abs=0.05)


def test_depletion_shrinks_under_forward_bias():
    assert ph.depletion_width(SI, 1e16, 1e16, 0.3) < ph.depletion_width(SI, 1e16, 1e16, 0.0)
    assert ph.depletion_width(SI, 1e16, 1e16, -5) > ph.depletion_width(SI, 1e16, 1e16, 0.0)


def test_depletion_rejects_too_much_forward_bias():
    with pytest.raises(ValueError):
        ph.depletion_width(SI, 1e16, 1e16, 5.0)


def test_diode_zero_and_reverse():
    assert ph.diode_current(0) == 0
    assert ph.diode_current(-1.0, i_s=1e-12) == pytest.approx(-1e-12, rel=1e-6)


def test_diode_forward_grows_exponentially():
    ratio = ph.diode_current(0.7) / ph.diode_current(0.6)
    assert ratio == pytest.approx(math.exp(0.1 / ph.thermal_voltage()), rel=0.01)


def test_mosfet_regions():
    assert ph.mosfet_current(0.5, 1.0, 0.7, 2e-4) == (0.0, "cutoff")
    i_tri, r1 = ph.mosfet_current(2.0, 0.2, 0.7, 2e-4)
    i_sat, r2 = ph.mosfet_current(2.0, 3.0, 0.7, 2e-4)
    assert (r1, r2) == ("triode", "saturation")
    assert i_sat == pytest.approx(0.5 * 2e-4 * 1.3**2)
    assert i_tri < i_sat


def test_mosfet_continuous_at_boundary():
    below, _ = ph.mosfet_current(2.0, 1.2999, 0.7, 2e-4)
    above, _ = ph.mosfet_current(2.0, 1.3, 0.7, 2e-4)
    assert below == pytest.approx(above, rel=1e-3)


def test_bad_inputs():
    with pytest.raises(ValueError):
        ph.thermal_voltage(0)
    with pytest.raises(ValueError):
        get_material("unobtainium")


def test_cli_commands(capsys):
    assert main(["intrinsic", "-m", "ge"]) == 0
    assert "Germanium" in capsys.readouterr().out
    assert main(["carriers", "--nd", "1e16"]) == 0
    assert "n-type" in capsys.readouterr().out
    assert main(["pn", "--na", "1e17", "--nd", "1e16"]) == 0
    assert "Vbi" in capsys.readouterr().out
    assert main(["mosfet", "--vgs", "2", "--vds", "3"]) == 0
    assert "saturation" in capsys.readouterr().out
    assert main(["diode", "-v", "0.65"]) == 0


def test_cli_error_code(capsys):
    assert main(["pn", "--na", "1e16", "--nd", "1e16", "--bias", "9"]) == 1
