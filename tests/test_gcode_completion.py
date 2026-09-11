"""Generated calibration jobs report completion after their cleanup."""

import pytest

from prusa_pa_tuner.flow_gen import FlowRampParams, build_flow_ramp
from prusa_pa_tuner.gcode_gen import SweepParams, build_sweep
from prusa_pa_tuner.probe_gen import ProbeParams, build_probe_test


@pytest.mark.parametrize(
    "build,params,prefix",
    [
        (build_sweep, SweepParams(), "PA"),
        (build_flow_ramp, FlowRampParams(), "FLOW"),
        (build_probe_test, ProbeParams(), "PROBE"),
        (build_probe_test, ProbeParams(probe_temp=150), "PROBE"),
    ],
    ids=["pa", "flow", "probe-cold", "probe-hot"],
)
def test_calibration_ends_with_completed_progress(build, params, prefix):
    gcode = build(params).gcode
    assert gcode.endswith(
        "M84 ; disable motors\n"
        "M73 P100 R0 ; print progress done\n"
        "M73 Q100 S0 ; print progress done\n"
    )
    assert gcode.index(f"M117 {prefix}_SWEEP_END") < gcode.index("M84")
