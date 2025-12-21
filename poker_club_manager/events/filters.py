from dataclasses import dataclass

from .models import Event


@dataclass(frozen=True)
class EventBrowseFilter:
    """
    Applies browse-time filtering and ordering
    to Event querysets based on user intent.
    """

    order: str = "relevance"
    include_finished: bool = False
    user_id: int | None = None

    def apply(self):
        """
        Entry point used by views.
        """
        qs = Event.objects.unfinished() if not self.include_finished \
                else Event.objects.all()
        return self._apply_order(qs)

    def _apply_order(self, qs):
        match self.order:
            case "newest":
                return qs.newest()

            case "oldest":
                return qs.oldest()

            case "popularity":
                return qs.popular()

            case "relevance":
                return qs.by_start_date()

            case _:
                return qs.by_start_date()
