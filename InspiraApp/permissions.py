from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    """
    Permission qui autorise uniquement le propriétaire de l'objet à le modifier.
    """

    def has_object_permission(self, request, view, obj):
        # Accès en lecture pour tous
        if request.method in SAFE_METHODS:
            return True

        # Accès en écriture uniquement pour le propriétaire
        return obj.user == request.user
