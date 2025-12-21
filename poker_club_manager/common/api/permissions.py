from rest_framework import permissions


class CanHost(permissions.BasePermission):
    message = "You do not have the required permissions."

    def has_permission(self, request, view):
        return request.user.can_host
