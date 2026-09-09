# Product Requirements Document

## 1. Product summary
HMM is an evidence-driven crypto market-intelligence platform. It focuses on detecting abnormal activity, verifying catalysts, and distinguishing trading momentum from investment quality.

## 2. User stories
- As a researcher, I want to see assets whose volume is accelerating relative to their own history.
- As a trader, I want to know whether price, volume, liquidity, and derivatives confirm one another.
- As an analyst, I want every catalyst claim linked to evidence and timestamped.
- As a user, I want the system to say "none found" instead of inventing an explanation.
- As a developer/agent, I want a machine-readable API for reports.
- As the project owner, I want payment/token integrations isolated behind explicit safety gates.

## 3. Functional requirements

### FR-1 Data ingestion
Collect normalized market observations from configurable providers.

### FR-2 Baselines
Maintain 7-day and 30-day rolling baselines for volume and other relevant metrics.

### FR-3 Anomaly detection
Flag conditions such as:
- 24h volume >= 2x 7-day average;
- 24h volume >= 3x 30-day average;
- volume / market cap > 15%;
- price >= +10% with expanding volume;
- rising participation before material price movement.

### FR-4 Research orchestration
For flagged assets, search supported sources for timestamped catalysts.

### FR-5 Evidence model
Every factual catalyst claim must retain source, timestamp, extraction time, and confidence metadata.

### FR-6 Classification
Catalysts:
- Confirmed
- Probable
- Speculative
- None found

### FR-7 HMM scoring
Produce independent scores for:
- Hype
- Metrics
- Mechanics
- Trading Opportunity
- Investment Quality
- Network Activity
- Catalyst Strength

### FR-8 API
Expose scan results and report objects through a versioned REST interface.

### FR-9 Bankr adapter
Support token-launch simulation behind a provider interface. The default environment must prohibit live execution.

### FR-10 Auditability
Persist decision inputs and scoring output sufficiently to reproduce a report.

## 4. Non-functional requirements
- Secrets never committed to source control.
- Provider failures fail gracefully.
- Reports identify stale/missing data.
- External calls use retry/backoff and timeouts.
- Core scoring logic is deterministic where practical.
- Test fixtures allow offline development.
- Live transaction paths require explicit configuration and human approval.

## 5. MVP acceptance criteria
A reviewer can clone the repository, run tests, execute an offline demo scan, inspect a generated report, and understand the architecture without possessing a wallet or API key.
