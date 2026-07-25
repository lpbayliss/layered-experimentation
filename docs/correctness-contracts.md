# Correctness contracts

This document closes distributed-systems, causal-provenance, and privacy ambiguities that are easy to miss in a conceptual experimentation design. These contracts are normative for any implementation. Numeric limits and infrastructure selections remain blocking decisions in the main specification.

## 1. Scope every identity

Every durable identifier and uniqueness constraint is scoped by:

```text
tenant + environment
```

The service must never compare, merge, hash into the same assignment space, or resolve relationships across environments or tenants unless a separately authorised export explicitly requests it.

The authoritative sticky assignment key is:

```text
tenant + environment + experiment_id + assignment_epoch +
canonical_randomisation_unit_hash
```

Request idempotency is separate:

```text
tenant + environment + caller_id + decision_point + idempotency_key
```

A repeated idempotency key with a different canonical request fingerprint is rejected. Concurrent requests lock assignment keys in deterministic sorted order and insert-or-read the same assignments in one transaction with the decision set and outbox records.

## 2. Revision and epoch taxonomy

Do not use one version number for unrelated concerns.

| Identifier | Changes when | Assignment consequence |
|---|---|---|
| `definitionRevision` | Any immutable experiment-definition edit | None by itself |
| `analysisRevision` | Exposure/trigger contract, metric, guardrail, estimand, attribution, or analysis-plan change | Does not rebucket; results and validity are segmented |
| `assignmentEpoch` | Eligibility cohort, randomisation unit, variant boundaries, treatment semantics, experiment slot set, or experiment salt changes | May change this experiment’s cohort/variant; analysed separately |
| `namespacePartitionEpoch` | Namespace unit, slot count, canonicalisation, namespace hash, or namespace salt changes | Potentially rebuckets the whole namespace; requires explicit migration |
| `allocationMapRevision` | Slot ownership/effective intervals change | Affects only changed ownership; never compacts other ranges |
| `configurationSequence` | Any published environment snapshot changes | Monotonic environment-wide publication order |

Metadata-only revisions do not enter either hash. Rollback publishes a **new** monotonic configuration sequence containing previously accepted content; an old sequence number is never made current again.

Every evaluation pins one complete configuration sequence. A decision cannot mix layer, eligibility, compatibility, or slot data from different sequences.

## 3. Configuration propagation and revocation

Each signed snapshot contains:

- tenant and environment;
- monotonic configuration sequence;
- parent sequence;
- creation and effective times;
- validity interval;
- minimum accepted sequence;
- namespace partition epochs and allocation map revisions;
- resolved compatibility/composition policy;
- signature algorithm/key ID and content digest.

### Default offline rule

Offline **first assignment is prohibited by default**. Cached reuse of an existing unexpired decision is allowed only by layer policy.

A future local-first mode requires all of:

- stable locally reproducible eligibility;
- deterministic provisional assignment ID;
- a bounded lease or allocation authority preventing conflicting first decisions;
- asynchronous insert-or-read reconciliation;
- quarantine when reconciliation disagrees;
- a stated maximum revocation delay.

A signed snapshot alone is insufficient authority for a sticky first assignment when different evaluators may observe different eligibility or configuration.

### Revocation precedence

Emergency revocation is a monotonic deny/tombstone feed independent of ordinary snapshots. It has precedence over cached assignment and configuration. A layer whose safety cannot tolerate the maximum revocation propagation interval must require online evaluation or fail closed.

A pause defines separately:

- whether new assignments stop;
- whether already assigned treatments may receive new exposures;
- the revocation effective time;
- cache invalidation and acknowledgement requirements;
- treatment of in-flight operations;
- analysis window marking.

## 4. Sticky and negative decision semantics

A positive control/treatment assignment is sticky for the experiment assignment epoch and exposure-validity window.

Negative results are not all equivalent:

| Result | Default persistence |
|---|---|
| `ineligible` from request-scoped/mutable attributes | Decision-set audit only; re-evaluated on a later operation |
| `ineligible` from declared stable cohort attributes | May be cached only for a bounded definition-revision validity |
| `namespace-miss` | Deterministic for the namespace partition epoch and unit; recomputable, not a permanent experiment assignment |
| `excluded` by concurrent context | Decision-set audit only; context may change |
| `revoked` / `fallback` | Operational fact with effective interval; never randomised control |
| positive control/treatment | Unique sticky assignment record |

An experiment requiring per-operation admission should randomise on an operation/request unit or separate stable assignment from a factual/counterfactual trigger. Long-lived identities must not silently enter and leave a cohort as mutable attributes change.

## 5. Slot ownership lifecycle

Namespace partitioning and experiment ownership are separate.

- A namespace partition epoch fixes unit type, canonicalisation, slot count, hash, and salt.
- Slot ownership has explicit `validFrom` and `validTo` under an allocation map revision.
- Changing an experiment’s slot set creates a new assignment epoch for that experiment and a churn report.
- Other experiments retain their slot ranges and assignment epochs.
- Ending an experiment closes new exposure at the declared time but never deletes historical assignment.
- Freed slots enter a configurable quarantine/washout interval before reuse when outcomes or treatment carryover can overlap.
- Reuse never causes the new experiment to inherit the old experiment’s assignment, exposure, or analysis identity.
- Namespace partition changes are high-impact migrations because they may rebucket every experiment; they require a separate ADR, dual evaluation, and staged cutover.

## 6. Full-set effect composition

Pairwise compatibility is necessary but insufficient. Before publication and at evaluation, validate the complete simultaneously applicable experiment set.

Each registered effect reducer declares:

- input and output types;
- identity value;
- associativity;
- commutativity;
- whether ordering matters;
- stable ordering key if needed;
- overflow/error behaviour;
- missing-value behaviour;
- maximum participant count;
- version and golden examples.

Two `replace` claims on the same effect are invalid. They cannot be waived by a generic compatibility override; an explicit versioned composition contract is required.

Eligibility uses a restricted deterministic DSL. Static intersection returns:

```text
proven-disjoint | may-overlap | invalid
```

`may-overlap` is treated as overlap and requires compatible complete-set composition or explicit exclusion. Arbitrary application code is not accepted as a proof of disjointness.

## 7. Historical explainability, not unlimited replay

The platform guarantees **explanation of the recorded decision**. It guarantees full re-execution only while the required protected inputs and relationship versions are retained.

A decision trace stores a minimized typed record of:

- configuration sequence and definition/assignment epochs;
- canonical randomisation unit token/hash;
- namespace slot and ownership interval;
- each eligibility predicate ID and boolean/unknown result;
- stable input references or protected typed values needed by policy;
- relationship-resolution IDs and versions;
- exclusion and complete-set compatibility results;
- variant interval and algorithm version;
- failure/cache/local mode;
- final effects and reason codes.

A plain hash is an integrity signal, not replay evidence. Low-entropy sensitive values must not be published as unsalted hashes. Use access-controlled encrypted snapshots or keyed digests where required.

Retention and lawful deletion may intentionally reduce replay capability. Audit responses must report when evidence was deleted and what weaker guarantee remains.

## 8. Causal context lineage

One token cannot assume that all decisions occur in one synchronous service call. Context is a server-side manifest:

```text
context_manifest_id
parent_manifest_ids[]
decision_set_ids[]
assignment_ids[]
exposure_ids[]
created_at
truncated
content_digest
```

SDK and service merge rules are deterministic:

1. verify tenant/environment and token scope;
2. take the union of referenced manifests;
3. deduplicate stable IDs;
4. sort canonically;
5. write a new immutable manifest when the inline bound would be exceeded;
6. mark `truncated=true` and emit quality telemetry if upstream lineage is unavailable.

Context tokens reference a manifest and may carry a bounded inline summary. They support parent/child fan-out, asynchronous messages, retries, and multiple independent layer decisions.

Attribution precedence is explicit:

1. direct exposure ID attached to the outcome;
2. direct assignment/decision context for intent-to-treat;
3. declared time-bounded unit relationships;
4. a named, versioned attribution-window rule.

The platform never guesses joins from current identity state. Missing or truncated lineage is visible and can invalidate primary analysis.

Assignment time, treatment-validity interval, exposure time, relationship-validity interval, outcome time, and ingestion time are stored separately.

## 9. Exposure is an observed fact

Remove the misleading idea that a remote service can atomically assign and prove exposure. The supported sequence is:

```text
decide → application successfully applies/observes effect → record exposure
```

A convenience helper may prepare an exposure envelope, but the application acknowledges only after the effect point succeeds. Intent-to-treat assignment remains available when exposure is missing.

Delivery mismatch is never rejected as data. Persist:

- intended assignment/effect;
- attempted delivery;
- actual effect or failure;
- mismatch reason;
- validity status for analysis.

The mismatch is quarantined from primary analysis and alerted, but the factual event remains immutable.

## 10. Event durability and idempotency

Every assignment, exposure, relationship, and outcome event contains:

- tenant/environment;
- globally unique immutable event ID;
- producer ID and producer-local sequence where available;
- schema version;
- event time and ingestion time;
- payload fingerprint;
- context manifest ID;
- optional supersedes/corrects event ID.

Duplicate same-ID/same-fingerprint delivery is a no-op. Same ID with a different fingerprint is quarantined and alerted. Corrections use new events; they do not overwrite facts.

SDK contracts define durable buffering, retry/backoff, bounded queue behaviour, shutdown flush, backpressure, and data-loss telemetry. Numeric queue and retry limits are production blockers, not implicit defaults.

If an effect is applied but exposure delivery fails, the SDK reports a durable pending/failure state. Analysis completeness metrics distinguish missing instrumentation from non-exposure.

## 11. Interaction eligibility

A co-exposure vector is evidence of concurrent treatment, not proof that an interaction is estimable.

An interaction report requires:

- compatible or explicitly mapped randomisation units;
- declared analysis unit and clustering;
- common eligibility/intersection definition;
- assignment, trigger, and actual-treatment overlap windows;
- factorial cell counts and SRM status;
- predeclared contrast where confirmatory;
- power/precision assessment;
- multiplicity policy;
- carryover/washout assumptions.

Report separately:

1. assignment interaction;
2. factual/counterfactual trigger interaction;
3. actual co-exposure interaction.

Higher-order combinations are validated for effect composition even when statistical reporting remains pairwise by default.

## 12. Privacy and token security

Opaque stable IDs remain pseudonymous personal data. Required controls include:

- per-tenant/environment tokenisation or keyed HMAC;
- purpose limitation and attribute allow lists;
- consent/opt-out or equivalent policy integration where applicable;
- residency and retention classification;
- access logging and least privilege;
- relationship-graph access controls;
- cross-environment isolation;
- key rotation and crypto-shredding policy.

Append-only means application facts are not silently mutated. It does not override lawful deletion. Erasure may use relationship-map deletion, encrypted-field crypto-shredding, tombstones, or irreversible aggregation. The resulting loss of reproducibility is recorded explicitly.

A decision-context token binds:

```text
tenant, environment, issuer, audience, schema version,
decision point, context manifest ID, issued time, treatment-validity interval,
key ID
```

It is an integrity-protected correlation capability, not an authorisation credential. Event ingestion verifies producer authority to reference the context and correlation units. Replay on an unrelated tenant, environment, producer, decision point, or unit is rejected. Signing-key verification history is retained for supported outcome windows.

## 13. Snapshot signatures and operational limits

A checksum detects accidental corruption; a signature establishes publisher authenticity. Published snapshots require both. The implementation ADR must define algorithm agility, trust roots, key rotation overlap, expiry, minimum sequence/rollback protection, and compromised-key response.

Before production, set and test limits for:

- treatment payload and event size;
- token inline size and manifest cardinality;
- units and experiments per decision request;
- eligibility expression depth/cost;
- composition participants;
- idempotency and assignment retention;
- late-event window and context lineage retention;
- SDK buffers and service backpressure.

Failure tests include multi-region partition, database unavailability, event-pipeline outage, key-service outage, clock skew, stale/corrupt snapshot, revocation lag, late events, and deleted relationship evidence.

## 14. Lifecycle semantics

The durable experiment owns identity and terminal archival. Each revision has approval status; only one assignment-affecting revision per experiment epoch may be active in an environment.

`paused → running` is allowed only by a new monotonic configuration sequence after compatibility, validity, and revocation checks. A completed experiment cannot resume; continuation creates a new assignment epoch or new experiment according to the analysis plan.

All authoritative decisions are committed before return. A response generated but not committed is not authoritative and must be retried through request idempotency.
