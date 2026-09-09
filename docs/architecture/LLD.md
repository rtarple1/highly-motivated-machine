# Low-Level Design

## Proposed Python packages

```text
hmm_core/
  models.py
hmm_providers/
  base.py
  coinbase.py
  market_data.py
  onchain.py
hmm_detection/
  baselines.py
  rules.py
hmm_research/
  orchestrator.py
  provenance.py
  classifier.py
hmm_scoring/
  hype.py
  metrics.py
  mechanics.py
hmm_reports/
  builder.py
hmm_integrations/
  bankr.py
  x402.py
hmm_api/
  main.py
```

## Core interfaces

### MarketProvider
- `list_assets()`
- `get_market_snapshot(asset)`
- `get_history(asset, window)`

### ResearchProvider
- `search(query)`
- `fetch(source)`
- `metadata(source)`

### ChainProvider
- `get_network_metrics(asset)`
- `get_holder_metrics(asset)`
- `get_flows(asset)`

### ExecutionProvider
- `simulate(request)`
- future production method must require policy approval

## Error strategy
Provider errors are typed and surfaced as missing/stale data. They must not silently convert into zero values.

## Report determinism
The report builder consumes a persisted observation/evidence bundle. This allows a reviewer to replay scoring without making external requests.
