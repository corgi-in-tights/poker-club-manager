from django.db import transaction

from .models import PointsLedger, SeasonMembership


def apply_scoring(event, deltas: dict, reason: str):
    with transaction.atomic():
        memberships = SeasonMembership.objects.select_for_update().filter(
            season=event.season,
            user_id__in=deltas.keys(),
        )
        membership_map = {m.user_id: m for m in memberships}

        for user_id, points in deltas.items():
            membership = membership_map.get(user_id)
            if not membership:
                continue

            membership.points += points
            membership.save(update_fields=["points"])

            PointsLedger.objects.create(
                membership=membership,
                event=event,
                points_delta=points,
                reason=reason,
            )
