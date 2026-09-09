# Highly Motivated Machine (HMM)
## SOP: Project Setup, GitHub Workflow, and HMM-001 Coinbase Provider

**Project:** Highly Motivated Machine (HMM)  
**Ticker concept:** `$HMM`  
**Brand personality:** “Trust Me Bro” / “Autonomous intelligence with trust issues”  
**Audience:** Beginner software developer  
**Milestones covered:** HMM-000 and HMM-001  
**Purpose:** Document exactly what was done, why it was done, how to reproduce it, and what was learned.

---

# 1. Purpose of This SOP

This SOP documents:

- **HMM-000 — Repository and Development Environment Setup**
- **HMM-001 — Coinbase Asset Provider**

The goal is not only to preserve commands, but to explain what each command, file, and engineering concept means.

---

# 2. What We Built

At the end of HMM-001, the project can:

- run as a structured Python project;
- run automated tests with `pytest`;
- use Git and GitHub;
- authenticate to GitHub using SSH;
- develop in feature branches;
- create and merge pull requests;
- connect to the Coinbase Exchange API;
- retrieve online crypto currencies;
- normalize Coinbase responses into HMM `Asset` objects;
- verify the provider using unit tests and a live smoke test.

The live test returned:

```text
Found 411 Coinbase crypto assets.
```

That number can change.

> Important: `/currencies` tells us about online Coinbase crypto currencies. It does **not** by itself prove that every returned asset is currently tradable on every Coinbase product or market. A later milestone will validate actual tradable products.

---

# 3. Repository Structure

```text
highly-motivated-machine-portfolio/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
├── src/
│   ├── hmm_core/
│   │   ├── __init__.py
│   │   └── models.py
│   └── hmm_providers/
│       ├── __init__.py
│       ├── base.py
│       └── coinbase.py
├── tests/
│   ├── test_models.py
│   └── test_coinbase_provider.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── MANIFEST.json
└── README.md
```

## Why this matters

- `src/` contains application code.
- `tests/` contains automated tests.
- `docs/` contains engineering documentation.
- `.github/` contains GitHub automation.
- root files contain configuration and project metadata.

This is much easier to scale than one large Python script.

---

# 4. HMM-000 — Initial Project Setup

## Step 1: Navigate to the project

```bash
cd ~/Documents/GitHub/highly-motivated-machine-portfolio
```

`cd` means **change directory**.

## Step 2: Initialize Git

```bash
git init
```

Git tracks project history.

## Step 3: Inspect status

```bash
git status
```

This shows your current branch, changed files, staged files, and sync state.

## Step 4: Stage files

```bash
git add .
```

The Git flow is:

```text
Modified → Staged → Committed
```

## Step 5: Create the first commit

```bash
git commit -m "Initial HMM project architecture and documentation"
```

A commit is a saved checkpoint in project history.

---

# 5. GitHub Repository

A GitHub repository was created for HMM.

Recommended name:

```text
highly-motivated-machine
```

Recommended description:

```text
Evidence-driven autonomous crypto market intelligence. Trust me, bro. HMM will check.
```

---

# 6. GitHub Authentication with SSH

## The problem

GitHub rejected ordinary account-password authentication for Git pushes over HTTPS.

## The solution

Use SSH authentication.

### Check for an existing key

```bash
ls -al ~/.ssh
```

Common files:

```text
id_ed25519
id_ed25519.pub
```

### Create a key if needed

```bash
ssh-keygen -t ed25519 -C "your-github-email@example.com"
```

### Start the SSH agent

```bash
eval "$(ssh-agent -s)"
```

### Add the key

```bash
ssh-add ~/.ssh/id_ed25519
```

### Copy the public key

```bash
pbcopy < ~/.ssh/id_ed25519.pub
```

Then add it in:

```text
GitHub → Settings → SSH and GPG keys → New SSH key
```

### Test authentication

```bash
ssh -T git@github.com
```

Successful output included:

```text
You've successfully authenticated
```

### Change the Git remote to SSH

```bash
git remote set-url origin git@github.com:rtarple1/highly-motivated-machine.git
```

Verify:

```bash
git remote -v
```

### Push main

```bash
git branch -M main
git push -u origin main
```

`origin` is the conventional name for the remote GitHub repository.

---

# 7. Python Virtual Environment

Create it:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install pytest:

```bash
pip install pytest
```

A virtual environment keeps this project's Python packages isolated.

---

# 8. Verify the Starter Tests

Run:

```bash
pytest
```

Initial result:

```text
2 passed
```

This confirmed the starter project was working before HMM-001 changes.

---

# 9. HMM-001 — Create a Feature Branch

```bash
git checkout -b feature/coinbase-provider
```

Verify:

```bash
git branch
```

Expected:

```text
* feature/coinbase-provider
  main
```

A feature branch isolates new work from stable `main`.

---

# 10. Create the Provider Package

Create:

```text
src/hmm_providers/
```

with:

```text
__init__.py
base.py
coinbase.py
```

`__init__.py` allows Python to treat the folder as a package.

---

# 11. Add the `Asset` Domain Model

File:

```text
src/hmm_core/models.py
```

Add:

```python
@dataclass(frozen=True)
class Asset:
    asset_id: str
    symbol: str
    name: str
    display_name: str | None = None
```

## Why this exists

Instead of letting raw Coinbase JSON spread through the application, HMM converts external data into its own internal representation.

Example:

```python
Asset(
    asset_id="BTC",
    symbol="BTC",
    name="Bitcoin",
    display_name="Bitcoin"
)
```

That is a **domain model**.

---

# 12. Normalization

The design is:

```text
External API
    ↓
Provider
    ↓
HMM canonical model
```

This is called **normalization**.

It allows HMM to eventually support multiple providers without rewriting the rest of the application.

---

# 13. Create the `AssetProvider` Abstraction

File:

```text
src/hmm_providers/base.py
```

Code:

```python
from abc import ABC, abstractmethod

from hmm_core.models import Asset


class AssetProvider(ABC):

    @abstractmethod
    def list_assets(self) -> list[Asset]:
        """Return assets available from the provider."""
        raise NotImplementedError
```

## Beginner explanation

Any HMM asset provider must implement:

```python
list_assets()
```

This establishes a contract.

Future implementations could include:

```text
AssetProvider
├── CoinbaseProvider
├── MockProvider
├── KrakenProvider
└── OtherProvider
```

This is **abstraction**: the rest of HMM depends on behavior, not on one vendor's implementation.

---

# 14. Create `CoinbaseProvider`

File:

```text
src/hmm_providers/coinbase.py
```

Core implementation:

```python
import json
import urllib.request

from hmm_core.models import Asset
from hmm_providers.base import AssetProvider


class CoinbaseProvider(AssetProvider):

    URL = "https://api.exchange.coinbase.com/currencies"

    def list_assets(self) -> list[Asset]:

        headers = {
            "User-Agent": "HMM/0.1",
            "Accept": "application/json",
        }

        request = urllib.request.Request(
            self.URL,
            headers=headers
        )

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            data = json.loads(
                response.read().decode()
            )

        assets = []

        for item in data:

            if (
                item.get("status") == "online"
                and item.get("details", {}).get("type") == "crypto"
            ):

                asset = Asset(
                    asset_id=item.get("id"),
                    symbol=item.get("id"),
                    name=item.get("name"),
                    display_name=item.get("details", {}).get("display_name"),
                )

                assets.append(asset)

        assets.sort(key=lambda asset: asset.symbol)

        return assets
```

---

# 15. Coinbase Provider Data Flow

```text
HMM
 ↓
CoinbaseProvider.list_assets()
 ↓
HTTP GET
 ↓
Coinbase /currencies
 ↓
JSON response
 ↓
filter online crypto entries
 ↓
convert to Asset
 ↓
sort
 ↓
return list[Asset]
```

---

# 16. Add the Provider Test

File:

```text
tests/test_coinbase_provider.py
```

Code:

```python
from hmm_providers.base import AssetProvider
from hmm_providers.coinbase import CoinbaseProvider


def test_coinbase_provider_is_asset_provider():
    provider = CoinbaseProvider()

    assert isinstance(provider, AssetProvider)
```

This verifies that `CoinbaseProvider` correctly follows the provider abstraction.

---

# 17. Debugging Lesson: Pytest Still Showed 2 Tests

At first, `pytest` still reported:

```text
2 passed
```

The new test file had not been saved in VS Code.

Fix:

```text
Command + S
```

Then rerun:

```bash
pytest -v
```

---

# 18. Debugging Lesson: `ImportError`

The next error was:

```text
ImportError: cannot import name 'Asset' from 'hmm_core.models'
```

Python found the module, but the `Asset` class was missing or unsaved.

Dependency chain:

```text
pytest
  ↓
test_coinbase_provider.py
  ↓
hmm_providers.base
  ↓
hmm_core.models
  ↓
Asset
```

After saving the `Asset` class:

```bash
pytest -v
```

returned:

```text
3 passed
```

---

# 19. Live Coinbase Smoke Test

A temporary file was created in the project root:

```text
demo_coinbase.py
```

Code:

```python
from hmm_providers.coinbase import CoinbaseProvider

provider = CoinbaseProvider()

assets = provider.list_assets()

print(f"Found {len(assets)} Coinbase crypto assets.")

for asset in assets[:20]:
    print(asset.symbol, "-", asset.name)
```

Run:

```bash
PYTHONPATH=src python demo_coinbase.py
```

`PYTHONPATH=src` tells Python to look in the `src/` directory for HMM packages.

---

# 20. Live Result

The provider successfully returned 411 online Coinbase crypto assets.

Example entries:

```text
00 - 00 Token
1INCH - 1Inch
AAVE - Aave
ADA - Cardano
AERO - Aerodrome Finance
AKT - Akash
ALCX - Alchemix
ALGO - Algorand
```

This proved that:

- the HTTP request worked;
- JSON parsing worked;
- filtering worked;
- `Asset` creation worked;
- sorting worked;
- the provider worked against the live API.

---

# 21. What the Smoke Test Did Not Prove

It did **not** prove that every returned asset is:

- actively tradable;
- available on every Coinbase product;
- available in every region;
- paired with USD;
- sufficiently liquid.

That is a later milestone.

---

# 22. Remove the Temporary Demo

```bash
rm demo_coinbase.py
```

The demo was temporary. Later, HMM will have a proper CLI or application entry point.

---

# 23. Final Test Before Commit

```bash
pytest -v
```

Expected:

```text
3 passed
```

---

# 24. Inspect, Stage, and Commit

Inspect:

```bash
git status
```

Stage:

```bash
git add .
```

Inspect again:

```bash
git status
```

Commit:

```bash
git commit -m "Add Coinbase asset provider"
```

This creates a permanent checkpoint for HMM-001.

---

# 25. Push the Feature Branch

```bash
git push -u origin feature/coinbase-provider
```

This uploads the feature branch to GitHub.

---

# 26. Create the Pull Request

Direction:

```text
feature/coinbase-provider → main
```

Title:

```text
HMM-001: Add Coinbase asset provider
```

The PR documented:

- what changed;
- why it changed;
- test results;
- known limitations.

---

# 27. Review Before Merge

Use the GitHub:

```text
Files changed
```

tab.

Check for:

- expected code changes;
- accidental files;
- exposed secrets;
- unexpected changes.

This is good practice even when working alone.

---

# 28. Merge the Pull Request

GitHub's default merge commit message was acceptable:

```text
Merge pull request #1 from rtarple1/feature/coinbase-provider
```

with:

```text
HMM-001: Add Coinbase asset provider
```

as the extended description.

---

# 29. Sync Local `main`

After merging on GitHub:

```bash
git checkout main
git pull origin main
git status
```

Ideal output:

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

---

# 30. Complete Development Workflow

```text
main
 ↓
feature branch
 ↓
write code
 ↓
test
 ↓
debug
 ↓
live smoke test
 ↓
git status
 ↓
git add
 ↓
git commit
 ↓
git push
 ↓
pull request
 ↓
review
 ↓
merge
 ↓
checkout main
 ↓
git pull
```

---

# 31. Engineering Concepts Learned

- **Git:** local version control.
- **GitHub:** remote repository hosting and collaboration.
- **SSH:** secure authentication to GitHub.
- **Branch:** isolated line of development.
- **Commit:** saved project checkpoint.
- **Pull request:** review and merge workflow.
- **Domain model:** HMM's internal representation of an asset.
- **Provider pattern:** isolates external API integrations.
- **Abstraction:** defines behavior without tying code to one provider.
- **Normalization:** converts vendor-specific data into canonical HMM data.
- **HTTP API integration:** communicates with Coinbase.
- **JSON parsing:** converts API responses into Python data.
- **Unit test:** checks expected behavior automatically.
- **Smoke test:** checks that a real integration works.
- **Import resolution:** how Python finds packages, modules, and names.

---

# 32. Interview Explanation

A concise explanation:

> I started HMM by separating external exchange integration from the application's domain model. I created a canonical Asset dataclass and an abstract AssetProvider contract, then implemented a Coinbase provider that retrieves online crypto currencies through the Coinbase Exchange API and normalizes the response into HMM Asset objects. I added pytest coverage, validated the integration against the live API, and delivered the feature through a Git feature-branch and pull-request workflow.

A simpler version:

> I turned an earlier standalone Coinbase API script into a reusable part of a larger application. Instead of spreading Coinbase-specific code throughout the project, I created a provider layer that translates Coinbase data into HMM's internal Asset model.

Do not claim full Coinbase trading availability validation yet.

---

# 33. HMM-001 Completion Checklist

- [x] Local Git repository configured
- [x] GitHub repository created
- [x] SSH authentication configured
- [x] Initial project pushed
- [x] Python virtual environment created
- [x] pytest installed
- [x] Feature branch created
- [x] `Asset` model created
- [x] `AssetProvider` abstraction created
- [x] `CoinbaseProvider` implemented
- [x] Provider test added
- [x] Automated tests passed
- [x] Live Coinbase smoke test passed
- [x] Feature committed
- [x] Feature pushed
- [x] Pull request created
- [x] Files reviewed
- [x] Pull request merged

**HMM-001 status: COMPLETE**

---

# 34. Next Milestone — HMM-002

## Market Data Provider

HMM currently has an asset directory.

The next milestone will enrich assets with data such as:

- price;
- market capitalization;
- fully diluted valuation;
- 24-hour volume;
- circulating supply;
- maximum supply.

Target architecture:

```text
CoinbaseProvider
      ↓
List[Asset]
      ↓
MarketDataProvider
      ↓
MarketObservation
```

Recommended start:

```bash
git checkout main
git pull origin main
git checkout -b feature/market-data-provider
```

---

# 35. Recommended Repository Location

Save this document as:

```text
docs/learning/01-project-setup-and-coinbase-provider.md
```

This gives the repository a permanent beginner-friendly engineering journal.

---

# 36. Final Learning Summary

The most important accomplishment was not simply retrieving Coinbase data.

We transformed:

```text
Standalone script
      ↓
Coinbase
      ↓
Output
```

into:

```text
HMM Application
      ↓
AssetProvider abstraction
      ↓
CoinbaseProvider
      ↓
Coinbase API
      ↓
Normalized Asset objects
```

That architecture is the foundation for HMM to grow into a multi-provider, evidence-driven market intelligence platform.
