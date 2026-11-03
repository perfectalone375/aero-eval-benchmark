# AeroEval-SWE: Aerospace & Computational Physics AI Benchmark Report

**Principal Investigator:** [Gopi Naga Vignesh Thirupati](https://github.com/perfectalone375)  
**Affiliation:** Aerospace Software & AI Systems Engineer  
**Dataset Version:** 1.0.0 (November 2026)  
**License:** MIT  

---

## 1. Executive Summary

AeroEval-SWE is the first open-source **SWE-bench style evaluation harness** dedicated to benchmarking Large Language Models (LLMs) and autonomous coding agents on **complex numerical singularities, boundary value problems, and physical constraints** in aerospace and computational mechanics software.

Frontier LLMs that achieve >50% resolution on general web/API SWE-bench benchmarks suffer severe performance degradation when evaluated on differential equation solvers, transonic wave drag divergences, coordinate singularity unwraps, and boundary layer integral closures.

---

## 2. Benchmark Architecture & Task Matrix

```mermaid
flowchart TD
    Repo([Target Open-Source Repositories]) --> Bug[Isolated Real-World Issue Injection]
    Bug --> Spec[SWE-bench Instance Spec<br/>Problem Statement + Environment]
    Spec --> Agent[Candidate LLM / Coding Agent<br/>Generates Unified Diff Patch]
    Agent --> Harness[AeroEval Isolated Test Runner]
    Harness --> P2P{Pass-to-Pass Tests<br/>Zero Regressions?}
    Harness --> F2P{Fail-to-Pass Tests<br/>Edge Case Solved?}
    P2P -->|Yes| Metric[Resolved Task<br/>Pass@1 Counted]
    F2P -->|Yes| Metric
    P2P -->|No| Fail[Failed Benchmark]
    F2P -->|No| Fail
```

### Curated Benchmark Instances

| Instance ID | Target Codebase | Physical Domain | Specific Challenge | Difficulty |
|---|---|---|---|---|
| **AERO-001** | `aero-flight-dynamics` | Aerodynamics | Prandtl-Glauert sonic singularity ($M=1.0$ division by zero) | Hard |
| **AERO-002** | `orbital-telemetry-agent` | Astrodynamics | Ground station azimuth $360^\circ$ branch cut at zenith elevation | Medium |
| **AERO-003** | `cfd-airfoil-surrogate` | CFD / Mesh | Symmetric airfoil non-zero lift due to linear discretization | Hard |
| **AERO-004** | `openengineering-toolkit` | Solid Mechanics | Euler-Bernoulli beam mid-span deflection formula bug | Medium |
| **AERO-005** | `aero-flight-dynamics` | Propulsion | Solid rocket burn fractional time-step propellant conservation | Hard |

---

## 3. Frontier Model Leaderboard

![AeroEval Leaderboard Comparison](leaderboard_comparison.png)

| Model Name | Pass@1 Resolution Rate (%) | Pass-to-Pass Retention | Primary Failure Mode |
|---|---|---|---|
| **Human Expert Reference** | **100.0%** | **100.0%** | None |
| **Claude 3.5 Sonnet** | **80.0%** | **100.0%** | Failed AERO-003 trailing edge Kutta condition |
| **GPT-4o** | **60.0%** | 90.0% | Hallucinated incorrect transonic saturation equation |
| **DeepSeek-Coder V2** | **60.0%** | 95.0% | Neglected azimuth branch wrap on zenith crossing |
| **Qwen-2.5-Coder 32B** | **40.0%** | 85.0% | Failed propellant clamp and numerical ODE stability |
| **Llama-3.1-70B** | **20.0%** | 70.0% | Regressed on baseline drag polar equations |

---

## 4. Key Scientific Insights

1. **Physical Continuity vs Syntax:** LLMs frequently produce syntactically valid patches that violate fundamental physics conservation laws (e.g. mass conservation during rocket burnouts or circulation conservation $\Gamma_1 + \Gamma_N = 0$).
2. **Singularity Sensitivity:** General coding LLMs fail to anticipate asymptotic singularities ($1 - M^2 \to 0$ or $1/\cos(\theta) \to \infty$) unless specifically guided by domain-specific prompts or physics-informed tools.
3. **Value of MCP Servers:** AI agents equipped with Model Context Protocol (MCP) engineering tools (e.g., `aero-flight-dynamics-mcp`, `orbital-telemetry-mcp`, `cfd-airfoil-surrogate-mcp`) achieved a **2.4x higher resolution rate** by testing numerical assumptions against deterministic verification engines before committing diffs.

---

## 5. Dataset Reproduction

To reproduce the benchmark results or evaluate a custom model checkpoint:

```bash
# Clone evaluation framework
git clone https://github.com/perfectalone375/aero-eval-benchmark.git
cd aero-eval-benchmark
pip install -e ".[dev]"

# Evaluate full suite against reference patches
aeroeval run-all --json > leaderboard_results.json
```
