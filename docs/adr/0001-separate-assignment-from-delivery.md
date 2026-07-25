# ADR-0001: Separate experiment assignment from feature delivery

- **Status:** Proposed
- **Date:** 2026-07-25

## Context

Feature-flag systems can target and bucket users, but experiment identity, allocation history, exposure, applied behaviour, and outcome attribution become difficult to govern when spread across flag rules and application data.

The target environment may continue using LaunchDarkly to deliver features, while a dedicated service owns experiment assignment.

## Decision

The experimentation service is the authoritative source for:

- eligibility;
- mutual exclusion and compatibility;
- deterministic assignment;
- treatment identity;
- assignment history and audit;
- decision-context propagation.

Feature delivery occurs after assignment. A delivery adapter receives an explicit treatment or exact-targeting key. It must not apply percentage bucketing independently.

The exposure event records both the assigned treatment and the concrete delivery variation/configuration actually used.

## Consequences

### Positive

- Stable experiment provenance independent of mutable flag rules.
- Delivery technology can change without changing causal identity.
- Assignment/delivery mismatch becomes detectable.
- Experiment definitions can govern non-flag treatments such as models, workflows, or policies.

### Negative

- A new critical service and SDK must be operated.
- Delivery adapters and migration tooling are required.
- Existing LaunchDarkly experiments need a staged shadow/comparison migration.

## Alternatives

- Keep LaunchDarkly authoritative: lowest initial effort, but does not solve the governing problem.
- Replace LaunchDarkly entirely: unnecessary scope; feature delivery is a different concern.
