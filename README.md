# HKD Optimizer - 1,000,000x ALU speedup

**Exact sparse incremental optimization — recompute what changed, not everything.**

HKD Optimizer is an exact incremental optimization framework powered by `hkd_alu`.

Many optimization systems repeatedly recompute millions of logical states even when a new event changes only a tiny portion of the problem. HKD Optimizer identifies the affected dependency state and evaluates only that active region while preserving exact agreement with the full reference computation.

The basic transformation is:

```text
Full recomputation:     O(N)
HKD incremental update: O(|A(Δ)|)
```

where `A(Δ)` is the dependency cone affected by a change `Δ`.

When:

```text
|A(Δ)| << N
```

the structural reduction can be enormous.

---

## Flagship Benchmark: Dynamic Semiconductor Job-Shop

A semiconductor-style scheduling workload models:

- processing times
- sequence-dependent setup times
- precedence
- Q-time constraints
- weighted tardiness
- dynamic production disruptions

A processing-time disruption may affect only a small dependency cone even though the complete scheduling state contains millions of operations.

Example result using the real `hkd_alu` backend:

```text
========================================================================================
HKD_INF_DYNAMIC_SEMICONDUCTOR_JOBSHOP_BENCHMARK
========================================================================================
logical operations     = 5,000,000
workcell blocks        = 156,250
ops / dependency cone = 32
disruption events      = 12
hkd_alu backend        = REAL MODULE

reference/full total   = 506.158 ms
HKD active total       = 135.183 us
measured speedup       = 3,744.23x
structural reduction   = 156,250.00x
exact equality         = PASS (12/12)
========================================================================================
```

### What the benchmark demonstrates

The reference evaluator recomputes all:

```text
5,000,000
```

logical scheduling operations after each disruption.

HKD identifies an affected state of only:

```text
32
```

operations.

That produces:

```text
5,000,000 / 32 = 156,250x
```

structural work reduction.

On the measured machine, this translated into:

```text
3,744.23x
```

wall-clock acceleration while preserving exact equality.

Structural reduction and measured wall-clock speedup are reported separately.

---

## Exact Incremental Update

Suppose a processing-time change `Δ` occurs at operation `i` in a fixed local precedence chain.

Completion times satisfy:

```text
C'_j = C_j          for j < i
C'_j = C_j + Δ      for j >= i
```

Therefore operations preceding `i` do not need to be recomputed.

If the dependency structure proves that other workcells cannot be affected, those workcells also remain unchanged.

HKD evaluates only the affected suffix and updates the global objective using exact delta arithmetic.

Conceptually:

```text
                         disruption Δ
                              |
                              v
                     dependency analysis
                              |
                              v
                       affected cone
                         A(Δ)
                              |
                              v
                          hkd_alu
                              |
                              v
                    exact delta evaluation
                              |
                              v
                      updated objective
                              |
                              v
                    exactness certificate
```

---

## Why This Matters

Optimization workloads commonly perform repeated evaluations during:

- dynamic scheduling
- local search
- neighborhood search
- simulation optimization
- routing
- resource allocation
- portfolio optimization
- production recovery
- machine-failure recovery
- cloud scheduling
- airline recovery

The complete optimization problem may be very large while consecutive states differ only slightly.

Traditional evaluation:

```text
evaluate(state_0)
evaluate(state_1)
evaluate(state_2)
...
```

can repeatedly process unchanged information.

HKD instead maintains persistent state:

```text
S(t+1) = S(t) + Δ(t)
```

and attempts to make computational work proportional to the state that actually changed.

---

# Applications

The framework is intended to support multiple optimization domains.

Current and planned examples include:

```text
examples/
├── semiconductor_jobshop.py
├── portfolio_repricing.py
├── opportunity_scoring.py
├── sparse_optimizer.py
├── airline_recovery.py
├── vehicle_routing.py
└── cloud_scheduling.py
```

The semiconductor dynamic job-shop benchmark is currently the flagship large-scale example.

---

# Installation

HKD Optimizer requires Python 3 and NumPy.

```bash
pip install numpy
```

Place `hkd_alu.py` somewhere importable by Python to use the HKD ALU backend.

The benchmark reports whether it found the real module:

```text
hkd_alu backend = REAL MODULE
```

---

# Quick Start

Run the standard test:

```bash
python3 tests/test.py
```

Example:

```text
HKD_OPTIMIZER
edition=free
logical_rows=100000
exact=True
structural_reduction_x=100,000
PASS
```

Run all tests:

```bash
python3 run_tests.py
```

---

# Free Edition

The free edition provides exact functionality for problems containing up to:

```text
1,000,000 logical rows
```

This allows developers and researchers to verify correctness and evaluate HKD incremental optimization on substantial workloads.

Run:

```bash
python3 tests/test.py
```

to verify the installation.

---

# Paid Edition

The paid edition removes the free logical-state limit.

Large workloads such as the semiconductor benchmark require the paid edition.

For example:

```bash
python3 tests/test_large.py
```

with the free edition produces:

```text
HKD_OPTIMIZER_PAID_REQUIRED
edition=free
logical_rows=5000000
free_limit=1000000
```

With the paid edition, the same large benchmark executes normally and verifies exact equality against full recomputation.

```text
edition                = paid
logical operations     = 5,000,000
ops / dependency cone = 32

reference/full total   = ...
HKD active total       = ...
measured speedup       = ...
structural reduction   = 156,250x
exact equality         = PASS
```

---

# Free vs. Paid

| Capability | Free | Paid |
|---|---:|---:|
| Exact incremental updates | Yes | Yes |
| Exactness verification | Yes | Yes |
| HKD active-state execution | Yes | Yes |
| Semiconductor example | Yes | Yes |
| Up to 1,000,000 logical rows | Yes | Yes |
| More than 1,000,000 logical rows | No | **Yes** |
| Large-scale benchmarks | No | **Yes** |
| Production-scale optimization | Limited | **Yes** |

The free edition is limited by **scale, not correctness**.

---

# Architecture

```text
Application
    |
    v
HKD Optimizer
    |
    +-- dependency cone
    |
    +-- persistent state
    |
    +-- exact delta evaluator
    |
    +-- certificate
    |
    v
HKD ALU
    |
    v
active-state execution
```

`hkd_alu` provides the underlying active-state execution primitive.

HKD Optimizer provides the optimization abstractions needed to turn sparse changes into exact incremental evaluations.

---

# Repository Structure

```text
hkd_optimizer/
├── README.md
├── requirements.txt
├── run_tests.py
│
├── hkd_optimizer/
│   ├── __init__.py
│   ├── edition.py
│   ├── incremental.py
│   ├── dependency.py
│   ├── certificate.py
│   └── benchmark.py
│
├── examples/
│   └── semiconductor_jobshop.py
│
├── benchmarks/
│   └── semiconductor_large.py
│
└── tests/
    ├── test.py
    └── test_large.py
```

---

# Benchmarking Rules

HKD Optimizer benchmarks follow several rules.

### 1. Exactness comes first

The HKD result must agree with the reference computation.

```text
exact equality = PASS
```

is required.

### 2. Structural reduction is not wall-clock speedup

These are reported separately.

For example:

```text
structural reduction = 156,250x
measured speedup     =   3,744x
```

A reduction in logical work does not imply an identical reduction in elapsed time.

### 3. Initial materialization is identified separately

Incremental optimization assumes persistent state exists from the preceding optimization state.

Initial construction costs must not be silently represented as incremental update costs.

### 4. Dependency locality must be justified

HKD may reuse an unchanged state only when the dependency structure establishes that the state cannot be affected by the current change.

---

# What HKD Optimizer Does Not Claim

The semiconductor benchmark demonstrates acceleration of **exact dynamic schedule re-evaluation**.

It does not by itself establish that arbitrary NP-hard optimization problems can be solved in polynomial or constant time.

A complete solver may perform:

```text
search
branching
propagation
candidate generation
constraint evaluation
objective evaluation
state management
```

HKD acceleration of one component translates into whole-solver acceleration according to how much execution time and logical work that component represents.

For that reason, HKD Optimizer distinguishes carefully between:

```text
structural work reduction
kernel wall-clock speedup
whole-application speedup
```

---

# Research Direction

The broader research question is:

> **When can exact dynamic optimization scale with the size of a disturbance rather than the size of the complete optimization state?**

Let:

```text
N      = complete logical problem size
Δ      = incoming change
A(Δ)   = exact dependency cone affected by Δ
```

The target complexity is:

```text
T(update) = O(|A(Δ)| polylog N)
```

rather than repeatedly paying:

```text
T(update) = O(N)
```

when most of the previous state remains valid.

For highly sparse dynamic workloads:

```text
|A(Δ)| << N
```

this distinction can be substantial.

---

# Philosophy

**Don't recompute the universe because one thing changed.**

HKD Optimizer attempts to preserve everything that remains provably valid and spend computation only on the state affected by the new event.

---

# Status

HKD Optimizer is experimental software.

Benchmark results are workload- and machine-dependent. Reproduce benchmarks on your own workloads and hardware before making production decisions.

---

# Related Project

HKD Optimizer is powered by `hkd_alu`, the active-state execution layer used by the incremental optimization engine.

---

# License

See `LICENSE` for distribution and commercial-use terms.
