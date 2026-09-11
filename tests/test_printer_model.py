"""The M862.3 model check must match the connected printer.

A wrong value makes Buddy reject the upload outright ("G-CODE is for a
different printer model"), so the model has to reach BOTH the header key
and the M862.3 assert in every generator that emits them.
"""
from prusa_pa_tuner.flow_gen import FlowRampParams, build_flow_ramp
from prusa_pa_tuner.gcode_gen import SweepParams, build_sweep
from prusa_pa_tuner.gcode_preamble import DEFAULT_PRINTER_MODEL, clean_printer_model
from prusa_pa_tuner.probe_gen import ProbeParams, build_probe_test


def _gcodes(model: str) -> dict[str, str]:
    return {
        "pa": build_sweep(SweepParams(printer_model=model)).gcode,
        "flow": build_flow_ramp(FlowRampParams(printer_model=model)).gcode,
        "probe": build_probe_test(ProbeParams(printer_model=model)).gcode,
    }


def test_model_reaches_header_and_assert():
    for name, gcode in _gcodes("MK4S").items():
        assert "; printer_model = MK4S" in gcode, name
        assert 'M862.3 P "MK4S" ; printer model check' in gcode, name


def test_default_is_core_one():
    """Core One is the primary target -- its bytes must not change."""
    for name, gcode in _gcodes(DEFAULT_PRINTER_MODEL).items():
        assert "; printer_model = COREONE" in gcode, name
        assert 'M862.3 P "COREONE" ; printer model check' in gcode, name


def test_unknown_but_wellformed_model_passes_through():
    """New Prusa models must work without waiting for a code change."""
    assert clean_printer_model("MK5") == "MK5"


def test_malformed_model_cannot_inject_gcode():
    """printer_model is interpolated into M862.3, so it is a trust boundary:
    a newline would emit standalone commands into a file the printer runs."""
    injected = 'MK4S" ; \nM104 S300'
    for bad in (injected, "", "   ", "MK4S\r\nG28", None):
        assert clean_printer_model(bad) == DEFAULT_PRINTER_MODEL, repr(bad)

    gcode = build_sweep(SweepParams(printer_model=injected)).gcode
    assert "M104 S300" not in gcode
    assert 'M862.3 P "COREONE" ; printer model check' in gcode
