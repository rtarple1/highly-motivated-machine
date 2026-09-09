from datetime import datetime, timezone
from hmm_core.models import MarketObservation


def test_volume_to_market_cap():
    obs = MarketObservation(
        asset_id="base:0xexample",
        observed_at=datetime.now(timezone.utc),
        price_usd=1.0,
        volume_24h_usd=20_000_000,
        market_cap_usd=100_000_000,
    )
    assert obs.volume_to_market_cap == 0.2


def test_volume_to_market_cap_without_market_cap():
    obs = MarketObservation(
        asset_id="base:0xexample",
        observed_at=datetime.now(timezone.utc),
        price_usd=1.0,
        volume_24h_usd=20_000_000,
    )
    assert obs.volume_to_market_cap is None
