# Highly Motivated Machine (HMM)
## SOP: HMM-002B — CoinGecko Market Data Provider

**Project:** Highly Motivated Machine (HMM)  
**Milestone:** HMM-002B  
**Audience:** Beginner software developer  
**Purpose:** Document how HMM added a real CoinGecko market-data provider, preserved provider abstraction, normalized live API data into the HMM domain model, tested the implementation, debugged failures, and validated the integration with a live BTC smoke test.

---

# 1. Milestone Objective

HMM-002A defined the internal market-data contract.

HMM-002B implemented the first real external market-data provider behind that contract.

The target architecture was:

```text
Asset
  ↓
CoinGecko ID Resolver
  ↓
CoinGecko API
  ↓
CoinGeckoProvider
  ↓
MarketObservation
```

The milestone goals were:

```text
1. Resolve an HMM asset to a CoinGecko identifier
2. Fetch real market data
3. Normalize provider-specific JSON
4. Return a canonical MarketObservation
5. Test parsing without depending on the live internet
6. Validate the provider with a real BTC request
```

---

# 2. Starting Checkpoint

Before HMM-002B began, HMM already had:

```text
HMM-001
Coinbase asset provider

HMM-002A
MarketObservation model
MarketDataProvider abstract interface
```

The automated test suite was at:

```text
5 passed
```

After the first CoinGecko resolver tests were added, the project reached:

```text
8 passed
```

After full CoinGecko provider implementation and parsing tests:

```text
10 passed
```

---

# 3. Why Asset Identity Matters

Crypto ticker symbols are not always unique.

A naive integration might do:

```text
symbol = "AI"
```

and assume there is only one asset called `AI`.

That can be dangerous.

Different projects may share a ticker symbol, exist on different chains, use similar names, or be wrapped or bridged versions of another token.

HMM therefore avoids blindly trusting ticker symbols when asking an external provider for market data.

The safer design is:

```text
HMM Asset
   ↓
Provider-specific mapping
   ↓
CoinGecko ID
```

---

# 4. File Created: `src/hmm_providers/coingecko.py`

The provider file was created at:

```text
src/hmm_providers/coingecko.py
```

The final implementation includes:

- a CoinGecko ID mapping
- an asset resolver
- a `CoinGeckoProvider`
- live HTTP request logic
- JSON normalization
- timestamp parsing
- provider provenance

---

# 5. Provider-Specific Asset Mapping

The initial mapping was intentionally small:

```python
COINGECKO_ID_BY_SYMBOL = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "AAVE": "aave",
    "AKT": "akash-network",
    "ALCX": "alchemix",
}
```

This creates deterministic mappings such as:

```text
BTC  → bitcoin
ETH  → ethereum
AKT  → akash-network
ALCX → alchemix
```

The important design choice is that HMM does not guess when a mapping does not exist.

---

# 6. Resolver Function

The resolver was implemented as:

```python
def resolve_coingecko_id(asset: Asset) -> str:
    coingecko_id = COINGECKO_ID_BY_SYMBOL.get(asset.symbol.upper())

    if coingecko_id is None:
        raise ValueError(
            f"No CoinGecko ID mapping found for asset: {asset.symbol}"
        )

    return coingecko_id
```

---

# 7. Why `.upper()` Is Used

The resolver calls:

```python
asset.symbol.upper()
```

This means:

```text
btc
BTC
Btc
```

all normalize to:

```text
BTC
```

That makes symbol lookup case-insensitive.

This behavior was later tested directly.

---

# 8. Why Unknown Assets Raise `ValueError`

Instead of:

```text
Unknown token
→ guess a CoinGecko result
```

HMM does:

```text
Unknown token
→ raise an explicit error
```

This supports a core HMM principle:

> Fail visibly rather than silently manufacture confidence.

For financial or market data, a clear failure is safer than confidently returning data for the wrong asset.

---

# 9. Why `coingecko_id` Was Not Added to the Core `Asset` Model

It would have been possible to modify the HMM domain model like this:

```python
@dataclass(frozen=True)
class Asset:
    ...
    coingecko_id: str
```

That was deliberately avoided.

The core `Asset` model should describe HMM's asset concept.

It should not need to know how one particular vendor identifies the asset.

Preferred separation:

```text
Asset
├── asset_id
├── symbol
├── name
└── display_name

CoinGeckoProvider
└── CoinGecko-specific IDs
```

This preserves provider independence.

Later HMM can support CoinGecko, DefiLlama, CoinMarketCap, or other providers without polluting the core model with vendor-specific fields.

This is an example of **separation of concerns**.

---

# 10. First CoinGecko Tests

The test file was created at:

```text
tests/test_coingecko_provider.py
```

The first resolver tests covered:

```text
BTC resolves to bitcoin
lowercase btc also resolves to bitcoin
unknown symbols raise ValueError
```

Example:

```python
def test_resolve_coingecko_id():
    asset = Asset(
        asset_id="BTC",
        symbol="BTC",
        name="Bitcoin",
    )

    assert resolve_coingecko_id(asset) == "bitcoin"
```

---

# 11. Case-Insensitive Resolver Test

```python
def test_resolve_coingecko_id_is_case_insensitive():
    asset = Asset(
        asset_id="btc",
        symbol="btc",
        name="Bitcoin",
    )

    assert resolve_coingecko_id(asset) == "bitcoin"
```

This verifies that normalization with `.upper()` works as expected.

---

# 12. Unknown Asset Test

```python
def test_resolve_coingecko_id_rejects_unknown_asset():
    asset = Asset(
        asset_id="UNKNOWN",
        symbol="UNKNOWN",
        name="Unknown Token",
    )

    with pytest.raises(ValueError):
        resolve_coingecko_id(asset)
```

This tests HMM's decision to reject unknown mappings rather than guess.

---

# 13. Debugging Issue: Test Filename

At one point, pytest was still reporting only:

```text
5 passed
```

The reason was that the CoinGecko test file name was incorrect.

Pytest discovers tests using naming conventions such as:

```text
test_*.py
```

After the file was renamed correctly to:

```text
test_coingecko_provider.py
```

pytest began trying to collect it.

This was a **test discovery issue**, not a business-logic failure.

---

# 14. Debugging Issue: Collection Syntax Error

After pytest found the file, collection failed with a syntax error.

The traceback pointed to:

```text
tests/test_coingecko_provider.py
line 18
```

The problem was:

```python
asset_id="UNKNOWN"
```

with a missing comma.

Correct version:

```python
asset_id="UNKNOWN",
```

Lesson:

> When pytest fails during collection, Python may not even be able to parse the test file yet.

---

# 15. Debugging Issue: Wrong Unknown Test Symbol

The unknown-asset test temporarily used:

```python
symbol="btc"
```

That would not be unknown.

The resolver intentionally converts:

```text
btc → BTC
```

and successfully maps BTC to Bitcoin.

The correct test data was:

```python
symbol="UNKNOWN"
```

This demonstrates the importance of designing test fixtures that actually exercise the intended behavior.

---

# 16. Reaching 8 Passing Tests

After the syntax and test-data issues were corrected, pytest reported:

```text
7 passed
```

Only two CoinGecko tests were present at that point.

The missing test was the case-insensitivity test.

After adding it, the suite reached:

```text
8 passed
```

---

# 17. Adding `CoinGeckoProvider`

The provider implements HMM's abstract interface:

```python
class CoinGeckoProvider(MarketDataProvider):
```

This matters because the rest of HMM can depend on:

```text
MarketDataProvider
```

rather than being tightly coupled to:

```text
CoinGeckoProvider
```

Conceptually:

```text
MarketDataProvider
       ↑
CoinGeckoProvider
```

---

# 18. CoinGecko Endpoint

The provider uses:

```python
BASE_URL = "https://api.coingecko.com/api/v3/coins/markets"
```

The request is built with query parameters equivalent to:

```text
vs_currency=usd
ids=bitcoin
```

For BTC, the final request conceptually becomes:

```text
/coins/markets?vs_currency=usd&ids=bitcoin
```

---

# 19. Building the Query

The implementation uses:

```python
urllib.parse.urlencode(
    {
        "vs_currency": "usd",
        "ids": coingecko_id,
    }
)
```

Using `urlencode()` is safer and clearer than manually concatenating query strings.

---

# 20. Standard-Library HTTP Client

HMM uses:

```python
urllib.request
```

rather than adding another dependency.

The request includes:

```python
headers={
    "User-Agent": "HMM/0.1",
    "Accept": "application/json",
}
```

and:

```python
timeout=10
```

The timeout prevents a request from hanging indefinitely.

---

# 21. Live Request Flow

Inside `get_market_observation()`, the provider does:

```text
Asset
 ↓
resolve CoinGecko ID
 ↓
build URL
 ↓
send HTTP request
 ↓
decode JSON
 ↓
validate payload
 ↓
parse first result
 ↓
return MarketObservation
```

---

# 22. Empty Payload Handling

The provider checks:

```python
if not payload:
    raise ValueError(
        f"No CoinGecko market data returned for asset: {asset.symbol}"
    )
```

This prevents code from blindly attempting `payload[0]` when there are no results.

---

# 23. Separation of Network I/O and Parsing

A major design decision was creating:

```python
_parse_market_observation()
```

instead of putting all conversion logic inside the HTTP method.

The responsibilities become:

```text
get_market_observation()
→ network I/O

_parse_market_observation()
→ data conversion
```

This is **separation of concerns**.

---

# 24. Why Parsing Was Split Out

If parsing only existed inside a live network call, every unit test would need to contact CoinGecko.

That would make tests slower, network-dependent, rate-limit-dependent, and less deterministic.

By separating parsing, HMM can test:

```text
fake CoinGecko JSON
        ↓
parser
        ↓
MarketObservation
```

without internet access.

---

# 25. Timestamp Parsing

CoinGecko returns an ISO timestamp similar to:

```text
2026-09-15T12:00:00.000Z
```

The provider converts it with:

```python
observed_at = datetime.fromisoformat(
    last_updated.replace("Z", "+00:00")
)
```

This converts `Z` into an explicit UTC offset so Python creates a timezone-aware `datetime`.

---

# 26. Why Timestamp Accuracy Matters

A market observation without time context is incomplete.

Later HMM milestones will compare values over time:

```text
observation history
       ↓
baseline
       ↓
current observation
       ↓
anomaly score
```

Therefore `observed_at` is required for historical analysis.

---

# 27. Missing Timestamp Handling

The parser checks:

```python
last_updated = data.get("last_updated")

if last_updated is None:
    raise ValueError("CoinGecko response is missing last_updated")
```

Rather than inventing a timestamp, HMM fails clearly.

---

# 28. CoinGecko-to-HMM Field Normalization

```text
CoinGecko                    HMM
------------------------------------------------
current_price             → price_usd
total_volume              → volume_24h_usd
market_cap                → market_cap_usd
fully_diluted_valuation   → fdv_usd
circulating_supply        → circulating_supply
max_supply                → max_supply
last_updated              → observed_at
provider identity         → source
```

This is **data normalization**.

---

# 29. Final Parser Structure

```python
return MarketObservation(
    asset_id=asset.asset_id,
    observed_at=observed_at,
    price_usd=data["current_price"],
    volume_24h_usd=data["total_volume"],
    market_cap_usd=data.get("market_cap"),
    fdv_usd=data.get("fully_diluted_valuation"),
    circulating_supply=data.get("circulating_supply"),
    max_supply=data.get("max_supply"),
    source="coingecko",
)
```

---

# 30. Required vs Optional Fields

Required values use:

```python
data["current_price"]
data["total_volume"]
```

Optional values use:

```python
data.get("market_cap")
data.get("max_supply")
```

This aligns with HMM's distinction:

```text
unknown / unavailable = None
known zero            = 0
```

---

# 31. Parser Test

A fake CoinGecko payload was created:

```python
data = {
    "current_price": 100_000,
    "total_volume": 40_000_000_000,
    "market_cap": 2_000_000_000_000,
    "fully_diluted_valuation": 2_100_000_000_000,
    "circulating_supply": 20_000_000,
    "max_supply": 21_000_000,
    "last_updated": "2026-09-15T12:00:00.000Z",
}
```

Then:

```python
observation = CoinGeckoProvider._parse_market_observation(
    asset,
    data,
)
```

The test checked each normalized field.

---

# 32. Why Fake API Data Is Useful

The test is not trying to verify CoinGecko itself.

It verifies HMM's code.

A provider unit test should answer:

> If CoinGecko gives us this payload, does HMM convert it correctly?

The test should not depend on CoinGecko uptime, internet connectivity, API rate limits, or current BTC price.

---

# 33. Defensive Timestamp Test

A second parser test provided market data without `last_updated`.

The test expected:

```python
pytest.raises(ValueError)
```

This verifies that timestamp validation works as designed.

---

# 34. Debugging Issue: Incorrect Field Mapping

After adding parser tests, the suite reported:

```text
1 failed, 9 passed
```

The failure was:

```text
assert observation.circulating_supply == 20_000_000
```

but the actual value was much larger.

The test revealed that the provider parser was mapping the wrong source value into `circulating_supply`.

This was corrected to:

```python
circulating_supply=data.get("circulating_supply"),
```

---

# 35. Why This Failure Was Valuable

Without the field-level assertion, incorrect financial data could have silently passed through HMM.

A weak test such as:

```python
assert observation is not None
```

would not catch incorrect market-field mappings.

The stronger test validates each important field individually.

---

# 36. Final Automated Test Result

After correcting the field mapping:

```bash
pytest -v
```

returned:

```text
10 passed
```

---

# 37. Live Smoke Test

Automated tests intentionally did not call the live CoinGecko API.

To validate the full real-world path, a temporary file was created:

```text
demo_coingecko.py
```

The script created a Bitcoin asset and called:

```python
provider = CoinGeckoProvider()
observation = provider.get_market_observation(asset)
```

---

# 38. Smoke Test Command

From the project root:

```bash
PYTHONPATH=src python demo_coingecko.py
```

`PYTHONPATH=src` tells Python to include the project's `src` directory when resolving imports.

---

# 39. Successful Live Result

The request succeeded and returned a real BTC observation, including:

```text
Asset: BTC
Observed at: 2026-09-15 21:15:20+00:00
Price (USD): 75804
24h Volume (USD): 39378210687
Market Cap (USD): 1522883952286
FDV USD: 1522894870765
Circulating Supply: 20084784.0
Max Supply: 21000000.0
Volume / Market Cap: 0.025857...
Source: coingecko
```

The exact market values are time-sensitive. What mattered was that the real API call succeeded, the fields were populated, the timestamp was timezone-aware, the computed ratio worked, and the source was `coingecko`.

---

# 40. Full Integration Proven by Smoke Test

```text
Asset("BTC")
    ↓
resolve_coingecko_id()
    ↓
"bitcoin"
    ↓
CoinGecko HTTP request
    ↓
JSON response
    ↓
_parse_market_observation()
    ↓
MarketObservation
```

---

# 41. Removing the Temporary Demo

After validation:

```bash
rm demo_coingecko.py
```

This keeps the repository clean.

---

# 42. Re-running Automated Tests After Cleanup

After deleting the demo:

```bash
pytest -v
```

Expected result:

```text
10 passed
```

---

# 43. Git Checkpoint

The implementation files were staged:

```bash
git add src/hmm_providers/coingecko.py tests/test_coingecko_provider.py
```

Committed:

```bash
git commit -m "Add CoinGecko market data provider"
```

Then pushed:

```bash
git push
```

The feature branch remains:

```text
feature/market-data-provider
```

---

# 44. Why HMM-002A and HMM-002B Share a Branch

HMM-002A defined the provider contract and market model.

HMM-002B implemented the first real provider.

Together they form:

```text
HMM-002 — Market Data Provider
```

Keeping them on the same feature branch creates a coherent pull request.

---

# 45. Current HMM Market Architecture

```text
CoinbaseProvider
      ↓
     Asset
      ↓
CoinGecko Resolver
      ↓
CoinGeckoProvider
      ↓
MarketObservation
```

This creates a clean distinction:

```text
Coinbase
→ asset universe / discovery

CoinGecko
→ market metrics
```

---

# 46. Architectural Principle: Provider Adapter

CoinGecko has its own API model.

HMM has its own domain model.

The provider acts as an adapter:

```text
CoinGecko representation
         ↓
CoinGeckoProvider
         ↓
HMM representation
```

This resembles the **Adapter Pattern**.

---

# 47. Architectural Principle: Dependency Inversion

Higher-level HMM logic can depend on:

```text
MarketDataProvider
```

instead of:

```text
CoinGeckoProvider
```

Example:

```text
Scanner
   ↓
MarketDataProvider
   ↑
   ├── CoinGeckoProvider
   ├── FutureProvider
   └── TestProvider
```

---

# 48. Architectural Principle: Provenance

Every observation includes:

```python
source="coingecko"
```

Later it will be possible to determine what value was observed, when it was observed, and which provider supplied it.

---

# 49. Architectural Principle: Fail Explicitly

Several HMM-002B choices intentionally reject bad or uncertain conditions:

```text
unknown mapping
→ ValueError

missing timestamp
→ ValueError

empty market payload
→ ValueError
```

This avoids silently degrading market intelligence quality.

---

# 50. Engineering Concepts Learned

- Provider abstraction
- Adapter pattern
- Normalization
- Separation of concerns
- Deterministic identity mapping
- Defensive programming
- Provenance
- Unit testing
- Smoke testing
- Test discovery
- Traceback debugging

---

# 51. Troubleshooting Summary

## Problem: Only 5 tests passed

Cause: CoinGecko test file was not named correctly for pytest discovery.

Resolution:

```text
tests/test_coingecko_provider.py
```

## Problem: Pytest collection error

Cause: missing comma after:

```python
asset_id="UNKNOWN"
```

Resolution:

```python
asset_id="UNKNOWN",
```

## Problem: Unknown asset test used BTC

Cause:

```python
symbol="btc"
```

was normalized and correctly resolved.

Resolution:

```python
symbol="UNKNOWN"
```

## Problem: Only 7 tests passed

Cause: case-insensitivity test had not yet been added.

Resolution: add the missing test.

## Problem: 1 failed, 9 passed

Cause: incorrect field mapping for `circulating_supply`.

Resolution:

```python
circulating_supply=data.get("circulating_supply"),
```

Final result:

```text
10 passed
```

---

# 52. Interview Explanation

> I implemented a CoinGecko market-data adapter behind an abstract MarketDataProvider interface. I added deterministic asset-to-provider ID mapping, normalized CoinGecko's response into our canonical MarketObservation model, preserved source provenance, separated network access from parsing for testability, and added defensive handling for unknown mappings, empty responses, and missing timestamps. I validated the implementation with ten automated tests and a live BTC API smoke test.

---

# 53. Beginner-Friendly Interview Follow-Up

If asked why CoinGecko JSON was not used directly:

> I wanted a stable internal contract. If I later replace CoinGecko or combine it with another provider, the scanner should not need to change everywhere. Only the provider adapter should need to know the external API's field names.

If asked why the live API was not part of pytest:

> Unit tests should be deterministic and fast. A live provider can be unavailable, rate-limited, or return changing values. I test the parser with controlled fake payloads and use a separate smoke test to verify live integration.

---

# 54. HMM-002B Completion Checklist

- [x] Created CoinGecko provider module
- [x] Added explicit CoinGecko ID mappings
- [x] Added case-insensitive resolver
- [x] Reject unknown mappings
- [x] Implemented `MarketDataProvider`
- [x] Added live HTTP request
- [x] Added request timeout
- [x] Added JSON decoding
- [x] Added empty-response validation
- [x] Separated parsing from HTTP logic
- [x] Parsed CoinGecko timestamp
- [x] Normalized CoinGecko fields
- [x] Added source provenance
- [x] Tested resolver
- [x] Tested case-insensitive resolution
- [x] Tested unknown-asset rejection
- [x] Tested full market parsing
- [x] Tested missing timestamp behavior
- [x] Fixed pytest file discovery issue
- [x] Fixed Python syntax error
- [x] Fixed invalid unknown-token test fixture
- [x] Fixed incorrect market-field mapping
- [x] Reached 10 passing automated tests
- [x] Completed live BTC smoke test
- [x] Removed temporary smoke-test file
- [x] Committed implementation
- [x] Pushed feature branch

**Milestone status: COMPLETE**

---

# 55. HMM-002 Overall Status

```text
HMM-002A
Canonical market model
+
Provider interface

HMM-002B
Real CoinGecko provider
+
Normalization
+
Testing
+
Live validation
```

Together:

```text
HMM-002 — Market Data Provider
```

---

# 56. What HMM Can Do Now

```text
discover a known crypto asset
        ↓
resolve its CoinGecko identity
        ↓
retrieve current market metrics
        ↓
convert them into a canonical snapshot
```

That snapshot includes:

```text
price
24h volume
market cap
FDV
circulating supply
max supply
timestamp
source
volume / market cap
```

---

# 57. What HMM Still Cannot Do Yet

HMM currently produces a market snapshot.

It does not yet know whether that snapshot is unusual.

For example:

```text
24h Volume = $40M
```

does not tell HMM whether $40M is normal, high, or extreme.

To know that, HMM needs history.

---

# 58. Recommended Next Milestone

## HMM-003 — Observation Storage

The next architectural step should be:

```text
MarketObservation
       ↓
Persistent Storage
       ↓
Observation History
```

That enables later:

```text
historical baselines
rolling averages
volume anomalies
market-cap-relative anomalies
HMM Radar
```

Likely sequence:

```text
HMM-003 → Observation Storage
HMM-004 → Historical Baselines
HMM-005 → Anomaly Detection
HMM-006 → HMM Radar CLI
```

---

# 59. Recommended Repository Location

Save this SOP as:

```text
docs/learning/03-coingecko-market-data-provider.md
```

The learning directory then becomes:

```text
docs/learning/
├── 01-project-setup-and-coinbase-provider.md
├── 02-market-data-model-and-provider-interface.md
└── 03-coingecko-market-data-provider.md
```

---

# 60. Suggested Git Workflow for This SOP

Copy the downloaded file into the repository:

```bash
cp ~/Downloads/HMM_SOP_HMM-002B_CoinGecko_Market_Data_Provider.md docs/learning/03-coingecko-market-data-provider.md
```

Then:

```bash
git add docs/learning/03-coingecko-market-data-provider.md
git commit -m "Document HMM-002B CoinGecko provider"
git push
```

---

# 61. Final Learning Summary

HMM-002B turned the market-data architecture from an interface into a functioning external integration.

The key design is:

```text
External API
   ↓
Provider Adapter
   ↓
Canonical HMM Model
   ↓
Future HMM Analytics
```

The engineering achievement is not simply:

> HMM can call CoinGecko.

It is:

> HMM can consume an external provider while keeping vendor-specific behavior isolated, preserving source provenance, validating critical fields, and returning a stable internal market-data contract that future analytics can depend on.
