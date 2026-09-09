import json
import urllib.request

from hmm_core.models import Asset
from hmm_providers.base import AssetProvider

class CoinbaseProvider(AssetProvider):
    
    URL = "https://api.exchange.coinbase.com/currencies"
    
    def list_assets(self) -> list[Asset]:
        
        headers = {
            "User-Agent":  "HMM/0.1",
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
                    display_name=item
                    .get("details", {})
                    .get("display_name"),
                )
                
                assets.append(asset)
        
        assets.sort(
            key=lambda asset: asset.symbol
        )
        return assets