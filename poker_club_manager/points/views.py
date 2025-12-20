from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


def leaderboard(request: HttpRequest):
    leaderboard_data = []
    return render(request, "points/leaderboard.html", {"leaderboard": leaderboard_data})

