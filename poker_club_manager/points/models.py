from django.db import models

from poker_club_manager.common.models import AbstractTimestampedModel


class PointsLedger(AbstractTimestampedModel):
    membership = models.ForeignKey(
        "common.SeasonMembership",
        on_delete=models.CASCADE,
        related_name="points_ledger",
    )
    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="points_ledger",
    )
    points_delta = models.IntegerField()
    reason = models.CharField(max_length=255)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["membership", "event"],
                name="unique_points_per_event",
            ),
        ]

    def __str__(self):
        return f"{self.membership_id} | {self.points_delta:+d} | {self.reason}"
