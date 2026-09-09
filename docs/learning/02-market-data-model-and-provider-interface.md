# Highly Motivated Machine (HMM)
## SOP: HMM-002A — Market Data Model and Provider Interface

**Project:** Highly Motivated Machine (HMM)  
**Milestone:** HMM-002A  
**Audience:** Beginner software developer  
**Purpose:** Document the exact steps used to expand HMM's market-data model, define a reusable market-data provider interface, test the changes, troubleshoot errors, and prepare the project for a real CoinGecko integration.

---

# 1. Milestone Objective

HMM-001 gave the project a way to retrieve a list of Coinbase crypto assets.

HMM-002A extends the architecture so HMM can represent **market data for an asset** and define a standard interface that any market-data provider must follow.

The goal of this milestone was:

```text
Asset
  ↓
MarketDataProvider
  ↓
MarketObservation
```

At this stage, HMM is **not yet connected to CoinGecko**. The purpose of HMM-002A is to define the internal contract first so external providers can plug into a stable HMM data model later.

---

# 2. Why We Defined the Model Before the API Integration

A common beginner approach is:

```text
Call API
  ↓
Use whatever JSON comes back
  ↓
Spread provider-specific fields everywhere
```

That works for small scripts but becomes difficult to maintain.

HMM instead uses:

```text
External Provider
      ↓
Provider Adapter
      ↓
Canonical HMM Model
```

This means CoinGecko, CoinMarketCap, DefiLlama, or another provider can all translate their data into the same HMM structure.

This is called **normalization** and is a core software-engineering concept.

---

# 3. Branch Used for HMM-002

The feature branch for this milestone is:

```text
feature/market-data-provider
```

If needed, it can be created with:

```bash
git checkout main
git pull origin main
git checkout -b feature/market-data-provider
```

## Why use a feature branch?

The `main` branch should remain stable.

New development happens on a separate branch:

```text
main
  \
   feature/market-data-provider
```

After the complete HMM-002 milestone is tested and reviewed, it will be merged back into `main`.

---

# 4. File Modified: `src/hmm_core/models.py`

The existing `MarketObservation` model was expanded.

The final relevant code became:

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


@dataclass(frozen=True)
class Asset:
    asset_id: str
    symbol: str
    name: str
    display_name: str | None = None


class CatalystClassification(str, Enum):
    CONFIRMED = "confirmed"
    PROBABLE = "probable"
    SPECULATIVE = "speculative"
    NONE_FOUND = "none_found"


@dataclass(frozen=True)
class MarketObservation:
    asset_id: str
    observed_at: datetime
    price_usd: float
    volume_24h_usd: float

    market_cap_usd: float | None = None
    fdv_usd: float | None = None

    circulating_supply: float | None = None
    max_supply: float | None = None

    source: str | None = None

    @property
    def volume_to_market_cap(self) -> float | None:
        if self.market_cap_usd in (None, 0):
            return None

        return self.volume_24h_usd / self.market_cap_usd


@dataclass(frozen=True)
class Evidence:
    claim: str
    source_url: str
    retrieved_at: datetime
    primary_source: bool
```

---

# 5. Understanding `MarketObservation`

A `MarketObservation` represents one market snapshot for one asset at one point in time.

Example conceptually:

```text
Asset: BTC
Observed at: 2026-09-09 14:00 UTC
Price: $100,000
24h Volume: $40B
Market Cap: $2T
FDV: $2.1T
Circulating Supply: 20M
Max Supply: 21M
Source: test
```

The key fields are described below.

---

# 6. `asset_id`

```python
asset_id: str
```

This identifies the asset the observation belongs to.

Example:

```python
asset_id="BTC"
```

Later HMM may use a more robust identifier including network and contract address because ticker symbols can collide.

---

# 7. `observed_at`

```python
observed_at: datetime
```

Market data changes constantly.

A value like:

```text
BTC = $100,000
```

is incomplete without a timestamp.

HMM needs to know **when** the data was observed so historical comparisons and baselines are meaningful.

---

# 8. `price_usd`

```python
price_usd: float
```

Stores the asset's current USD price at the time of observation.

---

# 9. `volume_24h_usd`

```python
volume_24h_usd: float
```

Stores the previous 24 hours of trading volume in USD.

This will become one of HMM's most important metrics because later milestones will compare current volume against historical baselines.

---

# 10. Optional Fields and the Meaning of `None`

Several fields use:

```python
float | None
```

Examples:

```python
market_cap_usd: float | None = None
fdv_usd: float | None = None
circulating_supply: float | None = None
max_supply: float | None = None
```

This means the value can either be a number or `None`.

`None` means HMM does not currently have a reliable value.

This is different from `0`, because zero means the value is known and actually zero.

---

# 11. `market_cap_usd`

```python
market_cap_usd: float | None
```

Market capitalization is generally:

```text
Price × Circulating Supply
```

It helps HMM understand the size of a cryptocurrency relative to others.

---

# 12. `fdv_usd`

```python
fdv_usd: float | None
```

FDV means **Fully Diluted Valuation**.

It estimates the value of the token if the full supply were circulating.

Conceptually:

```text
Price × Maximum or Total Supply
```

FDV is particularly useful in crypto because a token can have a small circulating market cap but a much larger future diluted valuation.

---

# 13. `circulating_supply`

```python
circulating_supply: float | None
```

Represents how many tokens are currently circulating in the market.

This will later help HMM evaluate dilution and token-unlock risk.

---

# 14. `max_supply`

```python
max_supply: float | None
```

Represents the maximum possible token supply when one exists.

Some cryptocurrencies do not have a hard maximum supply, so `None` may be valid.

---

# 15. `source`

```python
source: str | None
```

Records where the observation came from.

Examples could later include:

```text
coingecko
coinmarketcap
coinbase
defillama
```

This is an early form of **data provenance**.

---

# 16. The `volume_to_market_cap` Property

The model includes:

```python
@property
def volume_to_market_cap(self) -> float | None:
    if self.market_cap_usd in (None, 0):
        return None

    return self.volume_24h_usd / self.market_cap_usd
```

This calculates:

```text
24h Volume ÷ Market Cap
```

Example:

```text
24h Volume = $20M
Market Cap = $100M
```

Then:

```text
20M ÷ 100M = 0.20
```

or 20%.

---

# 17. Why Use `@property`?

With `@property`, HMM can use:

```python
observation.volume_to_market_cap
```

instead of:

```python
observation.volume_to_market_cap()
```

It behaves like a calculated field.

---

# 18. Why We Do Not Store the Ratio as a Field

If HMM stored the ratio separately, the numbers could disagree.

Example:

```text
Volume = 20M
Market Cap = 100M
Stored ratio = 0.90
```

That would be wrong.

By calculating the value dynamically, the ratio always reflects the stored volume and market cap.

---

# 19. File Modified: `src/hmm_providers/base.py`

The provider abstraction was expanded.

```python
from abc import ABC, abstractmethod

from hmm_core.models import Asset, MarketObservation


class AssetProvider(ABC):

    @abstractmethod
    def list_assets(self) -> list[Asset]:
        """Return assets available from the provider."""
        raise NotImplementedError


class MarketDataProvider(ABC):

    @abstractmethod
    def get_market_observation(
        self,
        asset: Asset,
    ) -> MarketObservation:
        """Return the latest market observation for an asset."""
        raise NotImplementedError
```

---

# 20. What `MarketDataProvider` Means

This class defines a rule:

> Any market-data provider used by HMM must be able to accept an `Asset` and return a `MarketObservation`.

Conceptually:

```text
Asset
  ↓
get_market_observation(asset)
  ↓
MarketObservation
```

---

# 21. Why This Is an Abstract Base Class

`MarketDataProvider` is a blueprint rather than a real provider.

Future implementations could include:

```text
MarketDataProvider
├── CoinGeckoProvider
├── CoinMarketCapProvider
├── MockMarketDataProvider
└── OtherProvider
```

---

# 22. Test Added to `tests/test_models.py`

```python
def test_market_observation_stores_extended_market_data():
    obs = MarketObservation(
        asset_id="BTC",
        observed_at=datetime.now(timezone.utc),
        price_usd=100_000,
        volume_24h_usd=40_000_000_000,
        market_cap_usd=2_000_000_000_000,
        fdv_usd=2_100_000_000_000,
        circulating_supply=20_000_000,
        max_supply=21_000_000,
        source="test",
    )

    assert obs.fdv_usd == 2_100_000_000_000
    assert obs.circulating_supply == 20_000_000
    assert obs.max_supply == 21_000_000
    assert obs.source == "test"
```

This verifies the new fields are stored correctly.

---

# 23. Test Added: `tests/test_market_data_provider.py`

```python
from hmm_providers.base import MarketDataProvider


def test_market_data_provider_is_abstract():
    assert MarketDataProvider.__abstractmethods__
```

This confirms the provider class is truly abstract.

---

# 24. First Test Run: Only 4 Tests Were Collected

The first run showed:

```text
collected 4 items
```

All four passed, but the new extended-market-data test was missing.

---

# 25. Why Pytest Did Not Discover the Fifth Test

The new function was accidentally indented inside another test.

Incorrect structure:

```python
def test_volume_to_market_cap_without_market_cap():
    ...

    def test_market_observation_stores_extended_market_data():
        ...
```

Because the second function was nested, pytest did not discover it as a top-level test.

---

# 26. Python Indentation Lesson

Python uses indentation as syntax.

Correct test structure:

```python
def test_one():
    pass


def test_two():
    pass
```

Each test should be defined at the module level unless nesting is intentional.

---

# 27. Second Test Run: 5 Tests Collected, 1 Failed

After fixing indentation, pytest found all five tests.

The fifth failed with:

```text
TypeError: MarketObservation.__init__() got an unexpected keyword argument 'volume_24_usd'
```

---

# 28. Why the `TypeError` Happened

The test used:

```python
volume_24_usd=40_000_000_000
```

but the model field is:

```python
volume_24h_usd
```

The missing letter was `h`.

Keyword argument names must match exactly.

---

# 29. Final Test Result

Run:

```bash
pytest -v
```

Final result:

```text
5 passed
```

The passing tests included:

```text
test_coinbase_provider_is_asset_provider
test_market_data_provider_is_abstract
test_volume_to_market_cap
test_volume_to_market_cap_without_market_cap
test_market_observation_stores_extended_market_data
```

---

# 30. What “5 Passed” Means

It means all currently defined automated checks completed successfully.

It does **not** mean HMM is finished or bug-free.

It means the behavior currently covered by those tests matches expectations.

---

# 31. HMM-002A Architecture After Completion

```text
AssetProvider
    ↓
Asset

Asset
    ↓
MarketDataProvider
    ↓
MarketObservation
```

Soon this becomes:

```text
CoinbaseProvider
      ↓
Asset
      ↓
CoinGeckoProvider
      ↓
MarketObservation
```

---

# 32. Git Checkpoint for HMM-002A

Because HMM-002A and HMM-002B belong to the same larger HMM-002 feature, keep working on:

```text
feature/market-data-provider
```

Create an intermediate checkpoint:

```bash
git status
git add .
git commit -m "Define market data model and provider interface"
```

This preserves a known-good version where HMM-002A has five passing tests.

---

# 33. Engineering Concepts Learned

- **Canonical Data Model:** HMM defines its own market-data format.
- **Normalization:** provider data is translated into HMM's internal representation.
- **Abstraction:** `MarketDataProvider` defines behavior without tying HMM to one vendor.
- **Interface / Contract:** providers must implement the required method.
- **Optional Data:** `None` represents unavailable values without pretending they are zero.
- **Computed Property:** `volume_to_market_cap` is calculated rather than stored redundantly.
- **Provenance:** `source` identifies where market data came from.
- **Unit Testing:** pytest verifies expected behavior.
- **Test Discovery:** test location and indentation affect whether pytest finds a test.
- **Python Indentation:** indentation changes program structure.
- **Keyword Arguments:** names passed to a constructor must match exactly.

---

# 34. How to Explain HMM-002A in an Interview

> In HMM-002A, I expanded the project's canonical market-data model to support market cap, FDV, circulating supply, max supply, source provenance, and a calculated volume-to-market-cap metric. I also introduced an abstract MarketDataProvider interface so external providers can return data in a consistent HMM format. I added tests for the new fields and provider contract and validated the milestone with five passing pytest tests.

Simpler version:

> I defined what market data should look like inside HMM before connecting another API. That way CoinGecko-specific fields do not spread throughout the application. Any future market-data provider must translate its data into the same MarketObservation object.

---

# 35. Troubleshooting Lessons

## Only 4 tests appeared

**Cause:** the new test was nested inside another test due to indentation.

**Fix:** move the new `def` to the top level.

## Fifth test failed with `unexpected keyword argument`

**Cause:** typo:

```text
volume_24_usd
```

instead of:

```text
volume_24h_usd
```

**Fix:** use the exact model field name.

---

# 36. HMM-002A Completion Checklist

- [x] Confirmed HMM-002 feature branch
- [x] Expanded `MarketObservation`
- [x] Added `fdv_usd`
- [x] Added `circulating_supply`
- [x] Added `max_supply`
- [x] Added `source`
- [x] Preserved `volume_to_market_cap`
- [x] Added `MarketDataProvider`
- [x] Added extended market-data test
- [x] Added provider abstraction test
- [x] Fixed pytest discovery issue
- [x] Fixed keyword-argument typo
- [x] Ran full test suite
- [x] Confirmed `5 passed`

**Milestone status: COMPLETE**

---

# 37. Next Milestone — HMM-002B

## CoinGecko Provider

Target architecture:

```text
CoinbaseProvider
      ↓
Asset
      ↓
CoinGeckoProvider
      ↓
MarketObservation
```

HMM-002B will introduce:

- CoinGecko API integration;
- mapping between HMM assets and CoinGecko IDs;
- parsing external market JSON;
- conversion into `MarketObservation`;
- provider-specific tests;
- live smoke testing;
- error handling.

---

# 38. Recommended Repository Location

Save this SOP as:

```text
docs/learning/02-market-data-model-and-provider-interface.md
```

Your learning folder will then contain:

```text
docs/learning/
├── 01-project-setup-and-coinbase-provider.md
└── 02-market-data-model-and-provider-interface.md
```

---

# 39. Final Learning Summary

HMM-002A did not add flashy market-scanning behavior.

Instead, it established a stable contract for future market data:

```text
Provider-specific data
        ↓
MarketDataProvider
        ↓
MarketObservation
        ↓
HMM business logic
```

That separation makes later code easier to test, replace, debug, and extend.
