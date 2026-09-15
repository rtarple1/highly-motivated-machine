import json
import urllib.parse
import urllib.request
from datetime import datetime

from hmm_core.models import Asset, MarketObservation
from hmm_providers.base import MarketDataProvider

COINGECKO_ID_BY_SYMBOL = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "AAVE": "aave",
    "AKT": "akash-network",
    "ALCX": "alchemix",
}

def resolve_coingecko_id(asset: Asset) -> str:
    coingecko_id = COINGECKO_ID_BY_SYMBOL.get(asset.symbol.upper())
    
    if coingecko_id is None:
        raise ValueError(
            f"No CoinGecko ID mapping found for asset: {asset.symbol.upper}"
        )
        
    return coingecko_id

class CoinGeckoProvider(MarketDataProvider):
    BASE_URL = "https://api.coingecko.com/api/v3/coins/markets"
    
    def get_market_observation(
        self,
        asset: Asset,
    ) -> MarketObservation:
        coingecko_id = resolve_coingecko_id(asset)
        
        query = urllib.parse.urlencode(
            {
                "vs_currency": "usd",
                "ids": coingecko_id,
            }
        )
        
        url = f"{self.BASE_URL}?{query}"
        
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "HMM/0.1",
                "Accept": "application/json",
            },
        )
        
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode())
            
        if not payload:
            raise ValueError(
                f"No CoinGecko market data returned for asset: {asset.symbol}"
            )
        
        return self._parse_market_observation(
            asset,
            payload[0],
        )    
        
    @staticmethod
    def _parse_market_observation(
        asset: Asset,
        data: dict,
    ) -> MarketObservation:
        last_updated = data.get("last_updated")
        
        if last_updated is None:
            raise ValueError("CoinGecko response is missing last_updated")
        
        observed_at = datetime.fromisoformat(
            last_updated.replace("Z", "+00:00")
        )
        
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
            
