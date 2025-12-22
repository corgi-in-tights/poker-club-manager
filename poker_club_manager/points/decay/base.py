from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from poker_club_manager.events.models import Event


class DecayStrategy(ABC):
    key: str

    @abstractmethod
    def calculate(self, event: "Event") -> dict[int, int]:
        """
        Apply points for this event.
        """
        raise NotImplementedError
