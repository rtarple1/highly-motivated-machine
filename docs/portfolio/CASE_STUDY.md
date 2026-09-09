# Portfolio Case Study — Highly Motivated Machine

## Elevator pitch
I designed HMM as an evidence-driven, agentic crypto market-intelligence platform that detects abnormal activity, researches potential catalysts, preserves source provenance, and produces independently scored trading and investment assessments.

## Engineering problem
Market intelligence comes from heterogeneous APIs and unstructured sources with mismatched identifiers, update frequencies, and trust levels. The system also has to prevent an AI-generated explanation from being mistaken for verified causality.

## Architecture decisions I can discuss in an interview
- canonical data contracts rather than coupling business logic to APIs;
- provider adapters for replaceability and offline testing;
- event/evidence provenance as a first-class entity;
- separate Hype, Metrics, and Mechanics scores;
- simulation-first financial integrations;
- human approval around irreversible actions;
- deterministic/replayable report scoring.

## Intended technologies
- Python
- FastAPI
- Pydantic/dataclasses
- SQL/PostgreSQL (SQLite for local demo)
- pytest
- GitHub Actions
- Docker
- REST APIs
- agent orchestration
- blockchain/on-chain APIs
- Bankr/x402 experiments

## What this project demonstrates
HMM is not presented as proof that an AI can predict markets. It demonstrates how to engineer a system that integrates noisy data, detects anomalies, orchestrates research, manages uncertainty, maintains provenance, and safely interfaces with financial infrastructure.

## Resume bullet — draft
Designed an agentic crypto market-intelligence platform using Python, REST APIs, normalized data contracts, anomaly detection, evidence provenance, and modular on-chain integrations; architected simulation-first financial workflows and human approval controls for safe interaction with token/payment infrastructure.
