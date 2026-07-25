# Migration from feature-flag-owned assignment

This plan moves experimental bucketing out of a feature-flag provider while keeping the provider for feature delivery. It avoids a one-step cutover that would rebucket active subjects or break historical attribution.

## Preconditions

- Inventory current experimental flags, targeting rules, variations, owners, assignment keys, and downstream outcome joins.
- Classify each flag as:
  - release/operational control;
  - experiment assignment;
  - treatment delivery;
  - permanent product configuration;
  - unknown/mixed concern requiring review.
- Identify active experiments that must preserve their current cohort until completion.
- Establish a mapping from existing assignment IDs/variations to durable experiment, revision, and variant IDs.

## Stage 1 — Observe current behaviour

Add an adapter that records, without changing behaviour:

- feature-flag key and revision;
- targeting/bucketing unit used;
- returned variation;
- application decision point;
- actual exposure point;
- concrete applied effect;
- outcome correlation token where available.

Do not label historical flag evaluation as actual exposure unless the treatment effect point is known.

## Stage 2 — Define the governing model

For each migrated experiment, declare:

- layer and effect claims;
- assignment unit;
- allocation namespace;
- current eligibility;
- current control/treatment mapping;
- compatibility and exclusions;
- safe failure policy;
- exposure point and outcome relationships.

If current bucketing cannot be reproduced, keep the active experiment on its existing mechanism until it ends. Do not silently move subjects mid-experiment.

## Stage 3 — Shadow assignment

Run the new assignment evaluator in shadow mode:

```text
existing feature-flag result → behaviour
new assignment result         → comparison telemetry only
```

Compare:

- eligibility;
- cohort membership;
- variant;
- assignment unit identity;
- persistence across requests;
- overlap vector;
- fallback behaviour;
- assignment-to-outcome joins.

Differences must be explained, not merely driven to zero: the existing rule may itself be inconsistent with the intended experiment.

## Stage 4 — Preserve or intentionally re-epoch cohorts

For an active experiment, choose one:

1. **Imported cohort:** materialise existing assignments as revision/epoch migration records and keep them sticky.
2. **Natural completion:** leave the experiment on the old system until it ends.
3. **New epoch:** start a separately analysed cohort after explicit approval; never blend results with the old assignment regime.

## Stage 5 — Make the experimentation service authoritative

The application requests assignment from the new SDK/service. LaunchDarkly receives an explicit treatment key or exact-targeting context and performs feature delivery only.

```text
Experiment service: eligible? → assigned variant → decision token
LaunchDarkly: deliver the exact component/configuration for that variant
Application: record actual applied effect
```

Percentage rollout and experiment bucketing rules must be removed from the delivery flag for that experiment.

## Stage 6 — Verify before expansion

For the first migrated layer, require:

- deterministic assignment golden tests;
- stable cohort checks across service restarts and config publication;
- assignment/exposure/applied-effect completeness;
- LaunchDarkly assignment/delivery mismatch alerts;
- SRM and overlap checks;
- service outage and safe-default tests;
- rollback to the previous delivery path without deleting evidence;
- analyst acceptance of canonical attribution data.

## Stage 7 — Retire mixed ownership

After all experiments for a flag have migrated or completed:

- remove percentage bucketing and experiment rules from LaunchDarkly;
- retain only delivery/operational controls;
- archive the assignment mapping and cutover revision;
- mark analytical windows affected by dual-running or rebucketing;
- remove temporary shadow telemetry after the agreed audit period.

## Rollback

If the new assignment path is unsafe:

1. Stop new authoritative assignments for the affected layer.
2. Apply the declared cached/safe-default/control policy.
3. Restore the prior feature-delivery path only if its assignment semantics and cohort impact are understood.
4. Preserve both systems’ decision and exposure facts.
5. Mark the affected data window; do not combine it into an ordinary experiment report.

Rollback is not permission to re-enable uncontrolled percentage bucketing for an active causal experiment.
