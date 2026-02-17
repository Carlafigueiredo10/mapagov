"""
Classes de permissao DRF para controle de acesso por role.

Hierarquia: operator < area_manager < general_manager < admin
Superusers passam em todas as checagens.
"""

from rest_framework.permissions import BasePermission
from processos.models_auth import is_approver


class IsAdminRole(BasePermission):
    """Exige role='admin' ou is_superuser."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return hasattr(request.user, 'profile') and request.user.profile.role == 'admin'


class IsAreaManagerOrAbove(BasePermission):
    """Exige role >= area_manager."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return hasattr(request.user, 'profile') and request.user.profile.has_role('area_manager')


class IsGeneralManagerOrAdmin(BasePermission):
    """Exige role >= general_manager."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return hasattr(request.user, 'profile') and request.user.profile.has_role('general_manager')


class IsApprover(BasePermission):
    """Aprovador: area_manager+ ou superuser (via is_approver)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and is_approver(request.user)
