"""Benchmark dataset schema and task registry for SWE-bench style engineering challenges."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class BenchmarkTask:
    instance_id: str
    repository: str
    domain: str
    difficulty: str
    problem_statement: str
    hints: str
    fail_to_pass_tests: list[str]
    pass_to_pass_tests: list[str]
    reference_patch: str

    def to_dict(self) -> dict:
        return asdict(self)


BENCHMARK_TASKS: list[BenchmarkTask] = [
    BenchmarkTask(
        instance_id="AERO-001",
        repository="aero-flight-dynamics",
        domain="Aerodynamics / Numerical Singularities",
        difficulty="Hard",
        problem_statement=(
            "Prandtl-Glauert compressibility correction in AeroCoefficients raises ZeroDivisionError "
            "or numerical infinity when flight velocity reaches Mach 1.0 (sonic singularity). "
            "Implement a smooth hyperbolic tangent (tanh) transonic saturation bridge connecting subsonic "
            "and supersonic wave drag regimes without discontinuity."
        ),
        hints="Check denominator 1 - Mach^2. Clip between Mach 0.95 and 1.05 using transonic wave drag model.",
        fail_to_pass_tests=[
            "test_transonic_drag_saturation_finite",
            "test_transonic_drag_monotonic_continuity",
        ],
        pass_to_pass_tests=["test_subsonic_drag_polar", "test_supersonic_wave_drag"],
        reference_patch="""--- a/src/aeroflight/coefficients.py
+++ b/src/aeroflight/coefficients.py
@@ -10,3 +10,6 @@ def compute_cd(mach: float, cd0: float) -> float:
-    beta = math.sqrt(1.0 - mach**2)
-    return cd0 / beta
+    if 0.95 <= mach <= 1.05:
+        return cd0 * 3.5 * math.tanh((mach - 0.95) / 0.1)
""",
    ),
    BenchmarkTask(
        instance_id="AERO-002",
        repository="orbital-telemetry-agent",
        domain="Astrodynamics / Coordinate Systems",
        difficulty="Medium",
        problem_statement=(
            "Ground station tracking azimuth angle undergoes 360-degree branch-cut discontinuity "
            "when satellite passes directly through the local zenith point (elevation > 89.9 deg). "
            "Add unwrapping logic to ensure smooth gimbal slewing commands."
        ),
        hints="Normalize azimuth difference using modulo 360 or atan2(sin(delta), cos(delta)).",
        fail_to_pass_tests=[
            "test_zenith_pass_azimuth_continuity",
            "test_gimbal_slew_rate_within_limits",
        ],
        pass_to_pass_tests=["test_horizon_acquisition_elevation", "test_doppler_shift_calculation"],
        reference_patch="""--- a/src/orbital_agent/tracking/pass_predictor.py
+++ b/src/orbital_agent/tracking/pass_predictor.py
@@ -25,2 +25,4 @@ def compute_azimuth_rates(azimuths: list[float]) -> list[float]:
-    diff = az[i] - az[i-1]
+    diff = (az[i] - az[i-1] + 180.0) % 360.0 - 180.0
""",
    ),
    BenchmarkTask(
        instance_id="AERO-003",
        repository="cfd-airfoil-surrogate",
        domain="Computational Fluid Dynamics / Discretization",
        difficulty="Hard",
        problem_statement=(
            "Vortex panel solver produces non-zero lift on symmetric NACA 0012 airfoil at alpha=0 "
            "due to unequal trailing-edge panel spacing in linear discretization. "
            "Replace uniform spacing with full cosine cluster discretization x = 0.5 * (1 - cos(theta))."
        ),
        hints="Enforce trailing edge Kutta condition closure: gamma_1 + gamma_N = 0.",
        fail_to_pass_tests=[
            "test_symmetric_airfoil_zero_lift_exact",
            "test_kutta_condition_trailing_edge",
        ],
        pass_to_pass_tests=["test_cambered_airfoil_lift_slope", "test_squire_young_profile_drag"],
        reference_patch="""--- a/src/cfd_surrogate/core/airfoil.py
+++ b/src/cfd_surrogate/core/airfoil.py
@@ -15,2 +15,3 @@ def generate_panels(n: int) -> np.ndarray:
-    return np.linspace(0.0, 1.0, n)
+    beta = np.linspace(0, np.pi, n)
+    return 0.5 * (1.0 - np.cos(beta))
""",
    ),
    BenchmarkTask(
        instance_id="AERO-004",
        repository="openengineering-toolkit",
        domain="Solid Mechanics / Analytical Formulas",
        difficulty="Medium",
        problem_statement=(
            "Euler-Bernoulli simply supported center-load deflection test hardcoded an erroneous "
            "denominator coefficient (96 vs correct 48), causing CI test failures. "
            "Update formula and test expectations to analytical P * L^3 / (48 * E * I)."
        ),
        hints="Check standard beam deflection tables: central point load max deflection delta = P*L^3 / (48*E*I).",
        fail_to_pass_tests=["test_center_load_max_deflection_exact"],
        pass_to_pass_tests=["test_center_load_max_moment", "test_bending_stress_magnitude"],
        reference_patch="""--- a/tests/test_beam.py
+++ b/tests/test_beam.py
@@ -16,1 +16,1 @@
-    assert simply_supported_center_load_max_deflection(1000, 2, 200e9, 1e-6) == pytest.approx(0.0004166666667)
+    assert simply_supported_center_load_max_deflection(1000, 2, 200e9, 1e-6) == pytest.approx(0.0008333333333)
""",
    ),
    BenchmarkTask(
        instance_id="AERO-005",
        repository="aero-flight-dynamics",
        domain="Propulsion & Ballistics / Numerical ODEs",
        difficulty="Hard",
        problem_statement=(
            "Solid rocket motor burn mass flow causes negative propellant mass when simulation time step "
            "dt exceeds residual burn time at burnout. "
            "Implement fractional-step burn cutoff clamp ensuring m_propellant >= 0.0."
        ),
        hints="Clamp burnout propellant to 0.0 and truncate thrust impulse proportionally.",
        fail_to_pass_tests=[
            "test_motor_burnout_propellant_non_negative",
            "test_exact_total_impulse_conservation",
        ],
        pass_to_pass_tests=["test_steady_state_thrust_profile", "test_sea_level_isp"],
        reference_patch="""--- a/src/aeroflight/motor.py
+++ b/src/aeroflight/motor.py
@@ -40,2 +40,3 @@ def step_burn(self, dt: float) -> float:
-    self.propellant_mass -= mdot * dt
+    consumed = min(self.propellant_mass, mdot * dt)
+    self.propellant_mass -= consumed
""",
    ),
    BenchmarkTask(
        instance_id="AERO-006",
        repository="aero-flight-dynamics",
        domain="6-DoF Kinematics / Gimbal Lock Singularities",
        difficulty="Hard",
        problem_statement=(
            "Euler angle extraction (Roll, Pitch, Yaw) from unit quaternions encounters gimbal lock singularity "
            "when pitch angle theta reaches +/- 90 degrees (|sin_theta| >= 1.0), producing division by zero "
            "or NaN in roll/yaw atan2 arguments. Implement singularity protection clamping."
        ),
        hints="Clamp sin_theta to [-1.0, 1.0]. When |sin_theta| >= 0.999999, set roll to 0.0 and compute yaw via 2-argument atan2.",
        fail_to_pass_tests=[
            "test_gimbal_lock_singularity_avoidance",
            "test_pitch_90_degree_finite_euler",
        ],
        pass_to_pass_tests=["test_quaternion_norm_preservation", "test_euler_roundtrip_subsonic"],
        reference_patch="""--- a/src/aero_flight_dynamics/trajectory/quaternions.py
+++ b/src/aero_flight_dynamics/trajectory/quaternions.py
@@ -102,4 +102,8 @@
-        pitch_rad = math.asin(sin_theta)
+        if abs(sin_theta) >= 0.999999:
+            pitch_rad = math.copysign(math.pi / 2.0, sin_theta)
+            roll_rad = 0.0
+            yaw_rad = math.atan2(-2.0 * (x * y - w * z), 1.0 - 2.0 * (y**2 + z**2))
""",
    ),
    BenchmarkTask(
        instance_id="AERO-007",
        repository="openengineering-toolkit",
        domain="Compressible Fluid Dynamics / Oblique Shock Waves",
        difficulty="Hard",
        problem_statement=(
            "The 2D supersonic oblique shock Theta-Beta-Mach solver diverges or produces unphysical roots "
            "when wedge deflection angle theta exceeds maximum attachment angle theta_max. "
            "Add golden-section theta_max pre-flight boundary check with explicit detachment exception."
        ),
        hints="Find maximum theta over beta in [mu, pi/2]. If theta > theta_max, raise ValueError indicating detached bow shock.",
        fail_to_pass_tests=[
            "test_oblique_shock_detachment_value_error",
            "test_theta_max_golden_section_bound",
        ],
        pass_to_pass_tests=["test_weak_oblique_shock_mach2", "test_isentropic_prandtl_meyer"],
        reference_patch="""--- a/src/openengineering/oblique_shock.py
+++ b/src/openengineering/oblique_shock.py
@@ -52,3 +52,6 @@
+    th_max_deg, _ = oblique_shock_max_theta_deg(m1, g)
+    if th > th_max_deg:
+        raise ValueError(f"Deflection theta exceeds maximum attachment angle theta_max={th_max_deg:.2f} deg.")
""",
    ),
    BenchmarkTask(
        instance_id="AERO-008",
        repository="orbital-telemetry-agent",
        domain="Astrodynamics / Orbital Transfers",
        difficulty="Medium",
        problem_statement=(
            "Orbital transfer optimizer hardcodes standard 2-impulse Hohmann transfers even when target orbit radius "
            "ratio r2/r1 exceeds 11.94, missing fuel-optimal 3-impulse bi-elliptic transfer solutions. "
            "Implement automated bi-elliptic threshold evaluation and delta-v comparison."
        ),
        hints="Calculate r2/r1 ratio. When r2/r1 > 11.94, evaluate 3-impulse bielliptic_transfer(r1, r2, rb) and set is_more_efficient_than_hohmann flag.",
        fail_to_pass_tests=[
            "test_bielliptic_crossover_efficiency",
            "test_bielliptic_3_impulse_conservation",
        ],
        pass_to_pass_tests=["test_hohmann_standard_leo_geo", "test_plane_change_impulse"],
        reference_patch="""--- a/src/orbital_telemetry/core/maneuvers.py
+++ b/src/orbital_telemetry/core/maneuvers.py
@@ -88,3 +88,6 @@
+    hohmann = hohmann_transfer(r1_km, r2_km, mu_km3_s2)
+    more_efficient = total_dv < hohmann.total_delta_v_km_s
+    return BiEllipticResult(..., is_more_efficient_than_hohmann=more_efficient)
""",
    ),
]


class BenchmarkRegistry:
    """Registry and lookup engine for aerospace SWE-bench instances."""

    @classmethod
    def get_task(cls, instance_id: str) -> BenchmarkTask | None:
        for t in BENCHMARK_TASKS:
            if t.instance_id.upper() == instance_id.upper():
                return t
        return None

    @classmethod
    def list_all(cls) -> list[BenchmarkTask]:
        return BENCHMARK_TASKS
