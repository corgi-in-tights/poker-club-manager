from dataclasses import dataclass

from .models import Event


@dataclass(frozen=True)
class EventListFilter:
    """
    Applies list-time filtering and ordering
    to Event querysets based on user intent.
    """

    search_query: str | None = None
    order: str = "relevance"
    include_finished: bool = False
    user_id: int | None = None

    def apply(self):
        """
        Entry point used by views.
        """
        qs = (
            Event.objects.unfinished()
            if not self.include_finished
            else Event.objects.all()
        )

        if self.search_query:
            qs = qs.search(self.search_query)

        return self._apply_order(qs)

    def _apply_order(self, qs):
        match self.order:
            case "date":
                return qs.by_start_date()

            case "popular":
                return qs.by_popularity()

            case "relevance":
                return qs.by_start_date()

            case _:
                return qs.by_start_date()
