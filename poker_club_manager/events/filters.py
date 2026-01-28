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
    annotate_details: bool = True

    def apply(self):
        """
        Entry point used by views.
        """
        qs = (
            Event.objects.all()
            if self.include_finished
            else Event.objects.unfinished()
        )
        if self.annotate_details:
            qs = qs.annotate_rsvp_count()
            if self.user_id:
                qs = (
                    qs.annotate_check_in(self.user_id)
                    .annotate_rsvp(self.user_id)
                    .annotate_check_in(self.user_id)
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
