from phoenix.incident import Incident
from phoenix.patching.patch import Patch
from phoenix.patching.strategies.unhandled_runtime import (
    UnhandledRuntimePatchStrategy
)


class PatchGenerator:
    def __init__(self):
        self.strategies = [
            UnhandledRuntimePatchStrategy()
        ]

    def generate(self, incident: Incident) -> list[Patch]:
        patches: list[Patch] = []

        for strategy in self.strategies:
            if strategy.supports(incident):
                patches.extend(strategy.generate(incident))

        return patches
