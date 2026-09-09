# ADR-003: Provider Adapters

**Status:** Accepted

## Context
Exchange, market, on-chain, social, and research providers change APIs, availability, pricing, and licensing.

## Decision
External dependencies sit behind small provider interfaces and map into HMM's canonical data model.

## Consequence
Business logic can be tested offline and providers can be replaced without rewriting the scoring system.
