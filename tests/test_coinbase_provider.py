from hmm_providers.base import AssetProvider
from hmm_providers.coinbase import CoinbaseProvider

def test_coinbase_provider_is_asset_provider():
    provider = CoinbaseProvider()
    
    assert isinstance(provider, AssetProvider)