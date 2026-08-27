# HKD Optimizer

Exact sparse dynamic re-evaluation for large optimization state spaces.

HKD Optimizer is designed for workloads where a small change affects only a small dependency cone inside a much larger logical problem. Instead of recomputing every logical row after each update, HKD maintains materialized state and re-evaluates only the active region required by the change.

The included semiconductor job-shop benchmark compares this incremental path against an exact full-reference recomputation and verifies equality after every disruption event.

## Highlights

- **Exact:** incremental results are checked against full-reference recomputation.
- **Sparse:** work scales with the active dependency cone rather than blindly revisiting the entire logical state.
- **Dynamic:** intended for repeated re-optimization after local changes, disruptions, or updates.
- **Portable:** tested on macOS and Linux.
- **Free edition:** supports up to **1,000,000 logical rows**.
- **Paid edition:** removes the logical-row limit.

> **Important:** reported speedups apply to the benchmarked dynamic evaluator/re-evaluation workload. They do not imply that every optimization problem, or an entire NP-hard solver, receives the same speedup.

## Quick Start

```bash
python3 run_tests.py
```

A successful paid-edition run includes:

```text
>>> tests/test.py
HKD_OPTIMIZER
edition=paid
logical_rows=100000
exact=True
structural_reduction_x=100,000
PASS

>>> tests/test_large.py
========================================================================================
HKD_INF_DYNAMIC_SEMICONDUCTOR_JOBSHOP_BENCHMARK
========================================================================================
edition                = paid
logical operations     = 5,000,000
workcell blocks        = 156,250
ops / dependency cone = 32
disruption events      = 4
hkd_alu backend        = COMPATIBILITY
initial materialize    = 119.428 ms

reference/full total   = 474.880 ms
HKD active total       = 120.285 us
measured speedup       = 3,947.96x
structural reduction   = 156,250.00x
exact equality         = PASS (4/4)
========================================================================================
test_large: PASS (paid)

ALL TESTS: PASS
```

Timing varies by machine and run. Exact equality and the structural work reduction are the key correctness properties; measured wall-clock speedup is hardware- and workload-dependent.

## Free vs. Paid

| Capability | Free | Paid |
|---|---:|---:|
| Exact functionality | Yes | Yes |
| Logical rows | Up to 1,000,000 | Unlimited* |
| `tests/test.py` | Yes | Yes |
| Large 5,000,000-row test | Upgrade boundary | Yes |
| Semiconductor benchmark | Up to free limit | Full scale |

\*Subject to available system resources.

### Edition boundary

`tests/test.py` verifies normal operation.

`tests/test_large.py` verifies the distribution boundary:

- **Free:** prints `HKD_OPTIMIZER_PAID_REQUIRED` for the paid-scale test.
- **Paid:** executes the **5,000,000 logical-operation** semiconductor benchmark and requires exact equality with the reference path.

## Benchmark: Dynamic Semiconductor Job Shop

The benchmark models a large logical manufacturing schedule divided into workcell blocks. Each disruption changes only a small dependency cone.

For each event, two paths are evaluated:

1. **Reference/full:** recompute the complete logical state.
2. **HKD active:** recompute only the dependency cone affected by the event.

Both paths must produce exactly the same result.

### 5,000,000 logical operations

Representative paid-edition result:

| Metric | Result |
|---|---:|
| Logical operations | 5,000,000 |
| Workcell blocks | 156,250 |
| Operations per dependency cone | 32 |
| Disruption events | 4 |
| Initial materialization | 119.428 ms |
| Full-reference total | 474.880 ms |
| HKD active total | 120.285 µs |
| Measured speedup | **3,947.96×** |
| Structural reduction | **156,250×** |
| Exact equality | **PASS (4/4)** |

The structural reduction follows directly from the benchmark shape: a full pass visits 5,000,000 logical operations while an active update touches a 32-operation dependency cone, giving `5,000,000 / 32 = 156,250×` fewer logical operations per event.

## Run the Standalone Benchmark

```bash
python3 benchmarks/semiconductor_large.py
```

Representative 1,000,000-operation output:

```text
========================================================================================
HKD_INF_DYNAMIC_SEMICONDUCTOR_JOBSHOP_BENCHMARK
========================================================================================
edition                = paid
logical operations     = 1,000,000
workcell blocks        = 31,250
ops / dependency cone = 32
disruption events      = 4
hkd_alu backend        = COMPATIBILITY
initial materialize    = 18.104 ms

reference/full total   = 65.297 ms
HKD active total       = 109.440 us
measured speedup       = 596.64x
structural reduction   = 31,250.00x
exact equality         = PASS (4/4)
========================================================================================
```

## Example

```bash
python3 examples/semiconductor_jobshop.py
```

Representative output:

```text
========================================================================================
HKD_INF_DYNAMIC_SEMICONDUCTOR_JOBSHOP_BENCHMARK
========================================================================================
edition                = paid
logical operations     = 1,000,000
workcell blocks        = 31,250
ops / dependency cone = 32
disruption events      = 4
hkd_alu backend        = COMPATIBILITY
initial materialize    = 17.754 ms

reference/full total   = 66.681 ms
HKD active total       = 98.533 us
measured speedup       = 676.74x
structural reduction   = 31,250.00x
exact equality         = PASS (4/4)
========================================================================================
```

## How It Works

For a logical state of size `N`, a conventional full re-evaluation may revisit all `N` rows after every event. If an event actually affects only `k` rows, HKD tracks the dependency structure and evaluates the active region instead.

Conceptually:

```text
full re-evaluation:   N rows / event
HKD active update:    k rows / event
structural reduction: N / k
```

In the 5,000,000-operation benchmark:

```text
N = 5,000,000
k = 32
N / k = 156,250x
```

This is a **structural work reduction**. Wall-clock speedup is lower because real execution includes Python overhead, indexing, state maintenance, function calls, memory effects, and other fixed costs.

## Project Layout

```text
.
├── benchmarks/
│   └── semiconductor_large.py
├── examples/
│   └── semiconductor_jobshop.py
├── hkd_optimizer/
├── tests/
│   ├── test.py
│   └── test_large.py
├── README.md
├── requirements.txt
└── run_tests.py
```

The distribution contains generated runtime files. The test and example entry points provide the public executable interface for validating behavior and reproducing the included benchmark.

## Buy Unlimited

Upgrade to the paid edition for unrestricted logical-row capacity:

**[Buy HKD Optimizer Unlimited](https://buy.stripe.com/fZu28k5uzcMv0ZcbV5gUM0k)**

The free edition remains exact; the paid edition removes the 1,000,000-logical-row product boundary so larger dynamic workloads can use the same evaluation model.

## Benchmark Interpretation

HKD Optimizer is most applicable when all of the following are true:

- a large state has already been materialized;
- updates are local relative to the full state;
- dependencies can be identified precisely;
- many updates or re-optimization events occur over the same evolving state; and
- exact equivalence to the corresponding full evaluation is required.

It is less useful when every update genuinely changes nearly the entire problem, when dependency locality is unavailable, or when one-time state construction dominates the workload.

## Reproducibility

When reporting benchmark results, include at least:

- HKD Optimizer edition;
- logical problem size;
- dependency-cone size;
- number of update/disruption events;
- initial materialization time;
- full-reference time;
- HKD active-update time;
- measured wall-clock speedup;
- structural reduction; and
- exact-equality result.

This keeps **algorithmic work reduction**, **measured runtime acceleration**, and **correctness** clearly separated.

## Correctness Standard

Performance is useful only if the active update preserves the reference result. The supplied benchmark therefore treats exact equality as a required condition:

```text
exact equality = PASS
```

A fast result that differs from the reference is not considered a successful benchmark.

---

**HKD Optimizer** — exact dynamic re-evaluation by doing the work that changed, rather than recomputing the state that did not.
