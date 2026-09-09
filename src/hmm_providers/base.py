from abc import ABC, abstractmethod
from hmm_core.models import Asset, MarketObservation

class MarketDataProvider(ABC):
    
    @abstractmethod
    def get_market_observation(
        self,
        asset: Asset,
    ) -> MarketObservation:
        """Return the latest market observation for an asset."""
        raise NotImplementedError

class AssetProvider(ABC):
   
    @abstractmethod
    def list_assets(self) -> list[Asset]:
        """Return assets available from the provider."""
        raise NotImplementedError