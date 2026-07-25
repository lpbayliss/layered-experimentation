# Specification review

**Verdict:** Conditionally ready for a technical prototype. Not ready for production implementation.

Reviewed against the repository’s stated requirements and the `agentic-software-specification` readiness checklist on 2026-07-25.

## Scores

`0 = absent`, `1 = weak/implicit`, `2 = clear`, `3 = strong and evidenced`.

| Area | Score | Evidence / gap |
|---|---:|---|
| Problem | 3 | Problem is separated from the solution and grounded in primary experimentation-platform sources. |
| Audience | 3 | Authors, application engineers, analysts, operators, security reviewers, and auditors are identified. |
| Scope | 3 | Goals, non-goals, assumptions, and phased delivery are explicit. |
| Requirements | 3 | Stable functional, quality, security, and invariant IDs with verification methods. |
| Quality | 2 | Correct scenario categories exist, but production SLO values and workloads are blocking. |
| Boundaries | 3 | Control plane, decision data plane, SDK, delivery adapter, and event/data plane are separated. |
| Behaviour | 3 | Assignment, exposure, triggering, outcome, overlap, idempotency, failure, rollout, and rollback flows are covered. |
| Design | 3 | Components, APIs, data contracts, hashing, slots, storage, and event flow are concrete. |
| Trade-offs | 3 | Credible alternatives include LaunchDarkly authority, SDK-only, service-only RNG, global layer, independent hashing, and factorial designs. |
| Security/privacy | 2 | Requirements and threats are explicit; retention, residency, RBAC, and treatment classification policies are unresolved. |
| Reliability | 2 | Failure modes and cached/snapshot modes exist; SLOs, capacity, store choice, and disaster-recovery targets are unresolved. |
| Operations | 2 | SLIs, data-quality signals, rollout, and rollback exist; dashboards, alert thresholds, and runbooks await implementation/SLOs. |
| Change safety | 3 | Immutable revisions, epochs, churn previews, fixed slots, snapshot rollback, and migration phases are specified. |
| Verification | 2 | Test categories and invariants are explicit; executable allocator/schema tests do not exist yet. Documentation checks are executable. |
| Traceability | 2 | Goals → requirements → architecture/ADRs → proposed implementation slices are linked conceptually; code/test traceability starts with implementation. |
| Agent readiness | 2 | Work is decomposed and blockers classified, but production tasks must wait for the named decisions. |
| Lifecycle | 2 | State machine, history, expiry, and launch-to-default exist; decision deadline and named specialist reviewers are not yet assigned. |

## Implementation-ready gate

### Satisfied for Phase 0 prototype

- Problem and boundaries are clear.
- Core invariants are explicit.
- Assignment/exposure/outcome semantics are defined.
- Architecture decisions and alternatives are recorded.
- Prototype tasks can be implemented without inventing business-domain behaviour.
- Documentation verification is executable.

### Blocking production implementation

- Assignment and propagation SLOs and reference workloads.
- Identity/unit-relationship ownership and retention.
- RBAC and approval policy.
- Authoritative store and event transport.
- Statistical owner and minimum sizing/SRM policy.
- Per-layer offline/cached first-assignment policy.
- Treatment payload classification.
- Independent specialist review from data science, privacy/security, and operations.

## Independent architecture review

A read-only distributed-systems review initially returned **not ready as an implementation contract**. The following findings were accepted and corrected:

| Finding | Resolution |
|---|---|
| Definition revision could rebucket subjects | Split definition, analysis, assignment, namespace-partition, allocation-map, and configuration versions |
| Persisted assignment identity incomplete | Tenant/environment-scoped global assignment key plus transactional insert-or-read |
| Mixed-unit namespace exclusion invalid | Each namespace binds exactly one randomisation unit type |
| Cached/offline reconciliation ambiguous | Offline first assignment prohibited by default; monotonic sequences, leases, revocation tombstones, and conflict quarantine specified |
| Hash could not replay eligibility | Guarantee narrowed to typed recorded-decision explanation; protected input/relationship retention governs full replay |
| Singular context token could not represent fan-out | Immutable mergeable context manifests with lineage, deduplication, bounds, and attribution precedence |
| Slot reuse and negative decisions undefined | Effective ownership intervals, experiment epochs, quarantine/washout, and negative-state persistence defined |
| Pairwise compatibility insufficient | Complete-set reducer validation and conservative eligibility DSL defined |
| Exposure and event contracts weak | Post-effect acknowledgement, immutable mismatch facts, event fingerprints, corrections, buffering, and loss telemetry defined |
| Interaction inference underspecified | Assignment/trigger/exposure interactions and estimability requirements separated |
| Privacy/deletion/token semantics incomplete | Pseudonymous-data controls, lawful-erasure mechanisms, scope-bound tokens, keyed digests, and replay-loss reporting defined |

The corrections are normative in [Correctness contracts](correctness-contracts.md).

## Review conclusion

Proceed only with an executable Phase 0 specification: schemas, canonical serialization, golden vectors, reference allocator, conflict validator, and property tests. The public repository is suitable as a reviewed design draft, **not** a production implementation contract. Do not commit to the production store, offline authority model, availability architecture, or analytical policy until the blocking decisions are resolved.
