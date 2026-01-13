"""Role-Based Access Control (RBAC) dependencies for FastAPI."""

from typing import Any, Callable, Dict, List

from fastapi import Depends, HTTPException, status

from src.adapter.rest.dependencies import get_current_user

# Valid roles in the system
VALID_ROLES = ["admin", "manager", "user", "viewer"]


def require_roles(allowed_roles: List[str]) -> Callable[..., Dict[str, Any]]:
    """
    Factory function that creates a dependency to check user roles.

    Creates a FastAPI dependency that validates the current user has one
    of the allowed roles. If the user's role is not in the allowed list,
    a 403 Forbidden error is raised.

    Args:
        allowed_roles: List of roles that are permitted to access the endpoint

    Returns:
        A dependency function that returns the current user if authorized

    Usage:
        @router.delete("/items/{id}")
        async def delete_item(
            current_user: dict = Depends(require_roles(['admin', 'manager']))
        ):
            ...
    """

    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        """
        Check if the current user has one of the allowed roles.

        Args:
            current_user: User data from JWT token

        Returns:
            User data if role is authorized

        Raises:
            HTTPException: 403 if user role is not in allowed_roles
        """
        user_role = current_user.get("role")
        user_email = current_user.get("email", "unknown")

        print(
            f"INFO [RBAC]: Checking role '{user_role}' for user '{user_email}' "
            f"against allowed roles {allowed_roles}"
        )

        if user_role not in allowed_roles:
            print(
                f"ERROR [RBAC]: Access denied for user '{user_email}' "
                f"with role '{user_role}'. Required: {allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}",
            )

        print(f"INFO [RBAC]: Access granted for user '{user_email}' with role '{user_role}'")
        return current_user

    return role_checker


def require_admin() -> Callable[..., Dict[str, Any]]:
    """
    Convenience dependency requiring admin role.

    Returns:
        Dependency that only allows admin users
    """
    return require_roles(["admin"])


def require_manager_or_above() -> Callable[..., Dict[str, Any]]:
    """
    Convenience dependency requiring manager or admin role.

    Returns:
        Dependency that allows admin and manager users
    """
    return require_roles(["admin", "manager"])


def require_user_or_above() -> Callable[..., Dict[str, Any]]:
    """
    Convenience dependency requiring user, manager, or admin role.

    Returns:
        Dependency that allows admin, manager, and user roles (excludes viewer)
    """
    return require_roles(["admin", "manager", "user"])


print("INFO [RBAC]: RBAC dependencies loaded")
