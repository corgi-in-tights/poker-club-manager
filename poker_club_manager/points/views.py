from types import SimpleNamespace

from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from poker_club_manager.common.models import Season
from poker_club_manager.common.utils.params import parse_int

from .filters import SeasonMemberListFilter


def leaderboard(request: HttpRequest, season_id: int | None = None):
    if season_id is not None:
        season = get_object_or_404(Season, id=season_id)
    else:
        season = Season.get_active_season()
        if not season:
            return render(
                request,
                "points/out_of_season.html",
            )

    default_filters = SimpleNamespace(
        {
            "order": "points",
            "members_per_page": 50,
            "search_query": "",
        },
    )

    search_query = request.GET.get("q", "").strip()
    order = request.GET.get("s", default_filters.order)

    members = SeasonMemberListFilter(
        search_query=search_query,
        order=order,
    ).apply(season)

    members_per_page = parse_int(
        request.GET.get("v"),
        default=default_filters.members_per_page,
        min_value=5,
        max_value=50,
    )

    paginator = Paginator(members, members_per_page)

    page = parse_int(
        request.GET.get("p"),
        default=1,
        min_value=1,
        max_value=paginator.num_pages,
    )
    page_members = paginator.get_page(page)

    context = {"members": page_members, "page": page, "max_page": paginator.num_pages}

    if request.headers.get("HX-Request") == "true":
        return render(request, "points/leaderboard.html#member_list", context=context)

    return render(
        request,
        "points/leaderboard.html",
        context={
            **context,
            "filters": SimpleNamespace(
                {
                    "order": order,
                    "members_per_page": members_per_page,
                    "search_query": search_query,
                },
            ),
            "default_filters": default_filters,
        },
    )


def archive(request: HttpRequest):
    seasons = Season.objects.filter(is_active=False).order_by("-start_date")
    return render(
        request,
        "points/archive.html",
        {"seasons": seasons},
    )
