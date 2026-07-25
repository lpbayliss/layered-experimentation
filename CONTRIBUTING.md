# Contributing

This repository is specification-first. Contributions should preserve the distinction between assignment, exposure, applied effects, and outcomes.

## Proposals

For a substantial change:

1. Open an issue describing the problem independently of the solution.
2. Identify affected requirements and invariants.
3. Add or update an ADR when the change is difficult to reverse.
4. Update examples and verification scenarios with the specification.

## Design requirements

- Do not introduce domain-specific concepts into the governing model.
- Do not use a feature-flag evaluation as authoritative experiment assignment.
- Do not infer exposure solely from assignment.
- Do not change hashing, slot allocation, or canonical serialization without a version and migration plan.
- New overlap behaviour must define conflict detection and interaction observability.
- Public examples must not contain proprietary or personally identifiable information.

## Intended implementation

The initial reference implementation is expected to use .NET. The protocol and persisted event contracts should remain language-agnostic.
