# ADR-002: Evidence Provenance Is a First-Class Entity

**Status:** Accepted

## Context
Crypto narratives often propagate faster than primary evidence. An LLM-generated explanation without provenance is not sufficient for investment research.

## Decision
Claims and evidence are stored separately. Reports cite evidence IDs; evidence retains source type, URL, event/publication time, retrieval time, and primary/secondary classification.

## Consequence
HMM can explicitly output "None found" when no reliable catalyst is available, and historical reports can be audited.
