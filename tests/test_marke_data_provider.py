from hmm_providers.base import MarketDataProvider

def test_market_data_provider_is_abstract():
    assert MarketDataProvider.__abstractmethods__
    