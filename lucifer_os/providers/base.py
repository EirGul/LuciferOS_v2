from abc import ABC, abstractmethod

from lucifer_os.registries.provider_registry import ProviderMetadata
from lucifer_os.response.response import LuciferResponse


class Provider(ABC):
    @abstractmethod
    def metadata(self) -> ProviderMetadata:
        raise NotImplementedError

    @abstractmethod
    def health(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def answer(self, prompt: str) -> LuciferResponse:
        raise NotImplementedError
