# ADR-001: Simulation-First Financial Integrations

**Status:** Accepted

## Context
HMM may integrate with token-launching and payment infrastructure. A portfolio demo must not accidentally broadcast transactions or require a reviewer to expose wallet credentials.

## Decision
All financial execution integrations default to simulation/read-only behavior. Live paths are disabled unless:
1. an explicit production environment flag is enabled;
2. required secrets are supplied securely;
3. a policy/human approval gate authorizes the action.

Bankr token-launch demonstrations use `simulateOnly: true`.

## Consequences
Positive:
- safer demos;
- easier testing;
- reduced accidental-loss risk;
- cleaner separation of research from execution.

Negative:
- production execution requires additional integration testing and controls.
