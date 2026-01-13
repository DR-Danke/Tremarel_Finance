"""Role-based access control dependencies for route protection."""

from typing import Any, Callable, Dict, List

from fastapi import Depends, HTTPException, status

from src.adapter.rest.dependencies import get_current_user


def require_roles(allowed_roles: List[str]) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """
    Create a dependency that checks if the current user has one of the allowed roles.

    Args:
        allowed_roles: List of role names that are allowed to access the route

    Returns:
        Dependency function that validates user role

    Example:
        @router.delete("/users/{id}")
        async def delete_user(
            current_user: dict = Depends(require_roles(['admin']))
        ):
            ...
    """

    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        """
        Check if user has one of the required roles.

        Args:
            current_user: Current authenticated user dict

        Returns:
            Current user dict if authorized

        Raises:
            HTTPException: 403 if user role is not authorized
        """
        user_role = current_user.get("role")
        print(f"INFO [RBAC]: Checking if role '{user_role}' is in allowed roles {allowed_roles}")

        if user_role not in allowed_roles:
            print(
                f"ERROR [RBAC]: User role '{user_role}' not authorized. "
                f"Required: {allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {', '.join(allowed_roles)}",
            )

        print(f"INFO [RBAC]: Role '{user_role}' authorized")
        return current_user

    return role_checker
