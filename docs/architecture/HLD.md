# High-Level Design

## Architecture goals
HMM should be modular, auditable, provider-agnostic, and safe to demonstrate without financial execution.

```mermaid
flowchart TB
    subgraph Sources
        EX[Exchange]
        MD[Market Data]
        OC[On-chain]
        DR[Derivatives]
        SO[Social]
        RS[Research Sources]
    end

    subgraph Platform
        ING[Provider Adapters]
        NORM[Normalization Layer]
        STORE[(Observation Store)]
        DET[Anomaly Detector]
        ORCH[Research Orchestrator]
        EVID[(Evidence Store)]
        SCORE[HMM Scoring Engine]
        REP[Report Builder]
    end

    subgraph Interfaces
        CLI[CLI]
        API[REST API]
        UI[Dashboard]
        X402[x402 Endpoint]
    end

    subgraph Controlled_Execution
        GATE[Human Approval / Policy Gate]
        BANKR[Bankr Adapter]
        SIM[Simulation Only by Default]
    end

    Sources --> ING --> NORM --> STORE --> DET --> ORCH
    RS --> ORCH
    ORCH --> EVID --> SCORE --> REP
    STORE --> SCORE
    REP --> CLI
    REP --> API
    REP --> UI
    API --> X402
    REP --> GATE --> BANKR --> SIM
```

## Key design principles
1. **Detection before narrative.**
2. **Evidence before confidence.**
3. **Independent scores instead of one opaque rating.**
4. **Provider abstraction to avoid vendor lock-in.**
5. **Financial execution isolated from analytical code.**
6. **Simulation-first by default.**
7. **Humans remain in the approval path for irreversible actions.**
