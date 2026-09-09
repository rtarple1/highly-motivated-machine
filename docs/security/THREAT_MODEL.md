# Initial Threat Model

## Assets to protect
- API keys
- wallet/private-key material
- treasury configuration
- user data
- research provenance
- report integrity
- execution permissions

## Key threats

### Secret leakage
**Risk:** committed `.env`, logs, exceptions, CI output.  
**Mitigation:** `.gitignore`, environment secrets, redaction, secret scanning.

### Prompt / content injection
**Risk:** malicious web/social content tries to alter agent behavior.  
**Mitigation:** treat retrieved text as untrusted data; separate instructions from evidence; allowlisted tools; schema validation.

### False catalyst attribution
**Risk:** model invents causality.  
**Mitigation:** evidence-backed classification; explicit `None found`; source/time alignment requirements.

### Asset identity collision
**Risk:** duplicate tickers cause wrong-chain/wrong-token analysis.  
**Mitigation:** canonical asset ID including network and contract where applicable.

### Accidental financial execution
**Risk:** test or demo launches a token or moves funds.  
**Mitigation:** simulation-first ADR; `HMM_LIVE_TRANSACTIONS=false`; human approval; separate execution credentials.

### Data poisoning / wash activity
**Risk:** manipulated social/on-chain activity inflates scores.  
**Mitigation:** provider diversity, quality flags, cross-source confirmation, anomaly explanation.

### Dependency / supply-chain compromise
**Mitigation:** pinned dependencies, automated vulnerability scans, minimal dependency surface.

## Security principle
**Analysis can be automated aggressively. Irreversible execution should be automated conservatively.**
