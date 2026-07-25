# ADR-0003: Separate assignment, exposure, applied effects, and outcomes

- **Status:** Proposed
- **Date:** 2026-07-25

## Context

A unit can be assigned to an experiment without reaching the code path where treatment changes behaviour. The intended treatment can also differ from what a feature-delivery or downstream system actually applies. Later outcomes may be recorded against a different but related unit.

Google’s overlapping-infrastructure paper distinguishes diverted traffic from the factual/counterfactual trigger set. Treating assignment as exposure dilutes triggered analyses and creates false attribution.

## Decision

Store four append-only fact types:

1. **Assignment:** authoritative treatment decision and configuration provenance.
2. **Exposure/trigger:** treatment actually reached the effect point, plus counterfactual trigger where required.
3. **Applied-effect manifest:** concrete values/components used by the application.
4. **Outcome:** later observable event with explicit decision context and unit relationships.

A signed decision-context token propagates identifiers through request and event chains. Attribution is a versioned derived model; it never rewrites the raw facts.

## Consequences

### Positive

- Supports intent-to-treat and triggered analyses explicitly.
- Proves which treatment configuration was used.
- Makes delivery mismatch and missing instrumentation visible.
- Supports outcomes recorded on different lifecycle entities.
- Preserves historical meaning after configuration changes.

### Negative

- More instrumentation and event volume.
- Requires schema governance and identity relationships.
- Exposure timing must be designed per effect point.
- Counterfactual triggering may require shared evaluator logic.

## Alternatives

- Assignment only: simple but analytically weak.
- Feature-flag evaluation event as exposure: convenient but often occurs before behavioural influence.
- Reconstruct applied values from current configuration: invalid after configuration changes.
