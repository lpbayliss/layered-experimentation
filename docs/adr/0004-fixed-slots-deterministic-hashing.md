# ADR-0004: Use fixed slot ownership and versioned deterministic hashing

- **Status:** Proposed
- **Date:** 2026-07-25

## Context

A simple weighted list of all active experiments reshuffles subjects when an experiment is added, removed, or resized. That violates the requirement that unrelated experiments remain unaffected.

Persisted random assignment avoids recalculation but creates a mandatory online data-store dependency and does not by itself ensure assignment independence across experiments.

## Decision

Each allocation namespace has a fixed versioned slot map. The namespace hash assigns a canonical unit to one slot. Experiments own explicit slot ranges; ended ranges become unallocated and are never compacted implicitly.

A separate experiment-ID/assignment-epoch salt selects the variant within an owned slot. Metadata revision is excluded from the hash; any assignment-affecting change must increment the epoch. Canonical serialization, hash algorithm, slot conversion, salts, and epochs are versioned and verified with golden vectors.

Authoritative first decisions are persisted for audit and idempotency. Deterministic evaluation remains the replay and policy-controlled offline mechanism.

## Consequences

### Positive

- Unrelated experiment add/remove operations cause zero assignment churn.
- Allocation collisions are statically detectable.
- Independent salts support orthogonal experiments.
- Historical decisions can be explained and independently replayed.

### Negative

- Slot fragmentation must be managed deliberately.
- Weight and eligibility changes require revision/epoch policy and churn preview.
- Canonical hashing is a public compatibility contract.
- Persisted first decisions add write load.

## Alternatives

- Compact global weighted ranges: rejected because unrelated changes rebucket subjects.
- Persisted RNG only: rejected as the default because it requires online storage for repeatability.
- Rendezvous/consistent hashing: useful for node membership, but removal would intentionally move subjects to other experiments and violate the stronger isolation invariant.
