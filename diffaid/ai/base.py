from abc import ABC, abstractmethod
from diffaid.models import ReviewResult

# Abstract Class for use with multiple different AI models
class ReviewEngine(ABC):
    @abstractmethod
    def review(self, diff: str) -> ReviewResult:
        pass