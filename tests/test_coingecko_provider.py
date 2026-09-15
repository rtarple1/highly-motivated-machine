import pytest
from hmm_core.models import Asset
from hmm_providers.coingecko import resolve_coingecko_id
from hmm_providers.coingecko import (
    CoinGeckoProvider,
    resolve_coingecko_id,
)

def test_resolve_coingecko_id():
    asset = Asset(
        asset_id="BTC",
        symbol="BTC",
        name="Bitcoin",   
    )
    
    assert resolve_coingecko_id(asset) == "bitcoin"
        
def test_resolve_coingecko_id_is_case_insensitive():
    asset = Asset(
        asset_id="btc",
        symbol="btc",
        name="Bitcoin",
    )
    
    assert resolve_coingecko_id(asset) == "bitcoin"
    
def test_resolve_coingecko_id_rejects_unknown_asset():
    asset = Asset(
        asset_id="UNKNOWN",
        symbol="UNKNOWN",
        name="Unknown Token",
    )
    
    with pytest.raises(ValueError):
        resolve_coingecko_id(asset)
        
        
def test_parse_market_observation():
    asset = Asset(
        asset_id="BTC",
        symbol="BTC",
        name="Bitcoin",
    )
    
    data = {
        "current_price": 100_000,
        "total_volume": 40_000_000_000,
        "market_cap": 2_000_000_000_000,
        "fully_diluted_valuation": 2_100_000_000_000,
        "circulating_supply": 20_000_000,
        "max_supply": 21_000_000,
        "last_updated": "2026-09-15T12:00:00.00Z",
    }
    
    observation = CoinGeckoProvider._parse_market_observation(
        asset,
        data,
    )
    
    assert observation.asset_id == "BTC"
    assert observation.price_usd == 100_000
    assert observation.volume_24h_usd == 40_000_000_000
    assert observation.market_cap_usd == 2_000_000_000_000
    assert observation.fdv_usd == 2_100_000_000_000
    assert observation.circulating_supply == 20_000_000
    assert observation.max_supply == 21_000_000
    assert observation.source == "coingecko"
    
def test_parse_market_observation_requires_last_updated():
    asset = Asset(
        asset_id="BTC",
        symbol="BTC",
        name="Bitcoin",
    )
    
    data = {
        "current_price": 100_000,
        "total_volume": 40_000_000_000,
    }
    
    with pytest.raises(ValueError):
        CoinGeckoProvider._parse_market_observation(
            asset,
            data,
        )