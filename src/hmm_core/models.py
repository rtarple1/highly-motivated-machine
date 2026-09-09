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

