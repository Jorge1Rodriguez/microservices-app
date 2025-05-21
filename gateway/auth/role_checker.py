from fastapi import HTTPException, Depends
from typing import List

from auth.jwt_handler import get_current_user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: dict = Depends(get_current_user)):
        if "role" not in current_user or current_user["role"] not in self.allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos suficientes para realizar esta acción"
            )
        return current_user
