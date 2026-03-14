from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    """
    Reusable role-based permission.
    Example:
      class AdminOnlyView(APIView):
          permission_classes = [HasRole]
          required_roles = {"admin"}
    """

    def has_permission(self, request, view):
        required = getattr(view, "required_roles", None)
        if not required:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return getattr(user, "role", None) in required
