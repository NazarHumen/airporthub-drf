from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """Object access limited to the ticket owner or an admin."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_admin or obj.user == request.user
