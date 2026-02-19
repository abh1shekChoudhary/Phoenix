from abc import ABC, abstractmethod
from phoenix.incident import Incident
from phoenix.patching.patch import Patch


class PatchStrategy(ABC):
    @abstractmethod
    def supports(self, incident: Incident) -> bool:
        pass

    @abstractmethod
    def generate(self, incident: Incident) -> list[Patch]:
        pass
