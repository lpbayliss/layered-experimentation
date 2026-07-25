# ADR-0002: Model layers, allocation namespaces, and effects separately

- **Status:** Proposed
- **Date:** 2026-07-25

## Context

Google’s overlapping infrastructure defines a layer as a subset of parameters that should not vary independently. In the target problem, teams use “layer” more broadly for a decision point or area of influence and sometimes need compatible experiments within that decision point.

Using one experiment per broad layer would waste traffic. Allowing all same-layer experiments to hash independently would permit silent conflicts.

## Decision

Represent three separate concepts:

1. **Layer:** semantic decision/influence and review boundary.
2. **Allocation namespace:** stable mutually exclusive slot space within a layer.
3. **Effect claim:** machine-readable behaviour an experiment may change and how it composes.

Experiments in one namespace are mutually exclusive. Experiments in different namespaces may overlap only when compatibility is mutual and effect claims are disjoint or use an approved deterministic composition operator.

Unknown eligibility intersections require review and are never assumed disjoint.

## Consequences

### Positive

- Layer names remain useful to humans.
- Compatible same-decision experiments can run concurrently.
- Mutual exclusion is mechanically enforceable.
- Conflicts and interaction context become explicit data.

### Negative

- More concepts than a single global bucket pool.
- Effect registry and taxonomy require governance.
- Compatibility cannot prove absence of causal interaction; analysis is still needed.

## Alternatives

- One global layer: simple but severely limits concurrency.
- One experiment per broad layer: safe but inefficient and too restrictive.
- Fully independent experiments: easy to run but unsafe and difficult to attribute.
- Full factorial configuration: explicit but combinatorially expensive.
