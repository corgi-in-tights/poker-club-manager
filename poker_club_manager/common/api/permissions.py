from rest_framework import permissions


class CanManageEvent(permissions.BasePermission):
    message = "You do not have the required permissions."

    def has_permission(self, request, view):
        return request.user.has_perm("events.manage_event")
