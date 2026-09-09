# Canonical Data Model

## Asset
- asset_id
- symbol
- name
- network
- contract_address
- exchange_status

## MarketObservation
- asset_id
- observed_at
- price_usd
- market_cap_usd
- fdv_usd
- volume_24h_usd
- circulating_supply
- max_supply
- source

## Baseline
- asset_id
- metric
- window_days
- mean
- median
- standard_deviation
- computed_at

## Signal
- signal_id
- asset_id
- signal_type
- observed_value
- baseline_value
- severity
- detected_at

## Evidence
- evidence_id
- asset_id
- claim
- source_url
- source_type
- published_at
- retrieved_at
- primary_source
- confidence

## Catalyst
- catalyst_id
- asset_id
- summary
- classification
- event_time
- evidence_ids

## HMMReport
- report_id
- asset_id
- generated_at
- hype_score
- metrics_score
- mechanics_score
- trading_score
- investment_quality_score
- network_activity_score
- catalyst_strength_score
- catalyst_classification
- confidence
- risks
- continuation_conditions
- invalidation_conditions
- evidence_ids
