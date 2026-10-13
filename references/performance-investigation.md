# Performance investigation (draft workflow)

Activation: a reported slowdown, resource regression or request to measure a proposed optimization.

Required evidence: representative inputs, environment, baseline command/results, repeated measurements, correctness contract and a profile or supported account of the work causing the cost.

Investigation: establish the slow path before changing it. Separate algorithmic work, I/O, database queries, initialization, caches and contention when relevant. Use comparable inputs and warm-up conditions. Record raw samples and alternate candidate/baseline order where helpful; avoid a single favorable timing.

Actions: for investigation, remain read-only unless a correction is authorized. Use synthetic or authorized workloads. Choose a focused candidate that preserves the actual contract; reduced work can still alter ordering, errors, memory usage or freshness. Do not run load tests on live services without applicable authorization.

Verification: check output equivalence and relevant regressions, then compare repeated timings and profiles. Operation counts establish work reduction, not latency or throughput. State input sizes, runtime, sample count and whether caching/concurrency/network behavior was exercised. Avoid timing assertions in unit tests unless a defensible environment-specific gate exists.

Failure handling: noisy samples, missing baselines, inaccessible production inputs or unrepresentative fixtures limit conclusions. Report an inconclusive or slower candidate without cherry-picking. Do not claim an agent benchmark improvement from a function microbenchmark.

Example: repeatedly scanning sales for every requested product can be replaced with a per-call aggregation over validated rows. Verify duplicate/missing requests and signed quantities; measure both implementations on the same synthetic data.

Failure case: aggregation processes rows that the old path never touched, potentially changing error behavior for malformed data. The validated-input assumption must be supported rather than invented for a real repair.

Expected output: supported cost cause, baseline/profile evidence, candidate and correctness checks if authorized, raw measurements and limitations. Agent-level behavior remains unverified.
