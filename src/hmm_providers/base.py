from abc import ABC, abstractmethod
from hmm_core.models import Asset

class AssetProvider(ABC):
    @abstractmethod
    def list_assets(self) -> list[Asset]:
        """Return assets available from the provider."""
        raise NotImplementedError