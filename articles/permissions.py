from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'profile') and request.user.profile.role == 'admin'

class IsEditor(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'profile') and request.user.profile.role == 'editor'

class IsReader(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'profile') and request.user.profile.role == 'reader'

class ArticlePermission(permissions.BasePermission):
    """
    Admin: CRUD sur tous les articles
    Editor: CRUD sur ses propres articles, lecture sur tous
    Reader: lecture seule
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated or not hasattr(request.user, 'profile'):
            return False
        role = request.user.profile.role
        if role == 'admin':
            return True
        if role == 'editor':
            if request.method in permissions.SAFE_METHODS:
                return True
            return True  # Détail géré dans has_object_permission
        if role == 'reader':
            return request.method in permissions.SAFE_METHODS
        return False

    def has_object_permission(self, request, view, obj):
        role = getattr(request.user.profile, 'role', None)
        if role == 'admin':
            return True
        if role == 'editor':
            if request.method in permissions.SAFE_METHODS:
                return True
            return obj.author == request.user
        if role == 'reader':
            return request.method in permissions.SAFE_METHODS
        return False
