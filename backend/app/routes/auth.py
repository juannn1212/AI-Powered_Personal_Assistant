from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
import re

from app.database import get_db
from app.models.user import User
from app.services.auth_service import (
    authenticate_user, 
    create_user, 
    get_current_user, 
    create_access_token,
    get_user_by_email,
    update_user_password
)
from app.schemas.auth import (
    UserLogin, 
    UserRegister, 
    UserResponse, 
    TokenResponse,
    PasswordReset,
    PasswordUpdate,
    UserUpdate
)

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Registra un nuevo usuario"""
    try:
        # Validar email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de email inválido"
            )
        
        # Verificar si el usuario ya existe
        existing_user = get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Validar contraseña
        if len(user_data.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña debe tener al menos 6 caracteres"
            )
        
        # Crear usuario
        user = create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        # Crear token de acceso
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                created_at=user.created_at
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Autentica un usuario y retorna un token"""
    try:
        # Autenticar usuario
        user = authenticate_user(db, user_data.email, user_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )
        
        # Verificar si el usuario está activo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cuenta desactivada"
            )
        
        # Crear token de acceso
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                created_at=user.created_at
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/forgot-password")
async def forgot_password(email: str, db: Session = Depends(get_db)):
    """Envía un email para restablecer la contraseña"""
    try:
        # Verificar si el usuario existe
        user = get_user_by_email(db, email)
        if not user:
            # Por seguridad, no revelar si el email existe o no
            return {"message": "Si el email existe, se enviará un enlace de restablecimiento"}
        
        # En un entorno real, aquí se enviaría un email
        # Por ahora, solo retornamos un mensaje de éxito
        return {
            "message": "Se ha enviado un enlace de restablecimiento a tu email",
            "email": email
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """Restablece la contraseña del usuario"""
    try:
        # Verificar si el usuario existe
        user = get_user_by_email(db, reset_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Validar nueva contraseña
        if len(reset_data.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña debe tener al menos 6 caracteres"
            )
        
        # Actualizar contraseña
        success = update_user_password(db, user.id, reset_data.new_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar la contraseña"
            )
        
        return {"message": "Contraseña actualizada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtiene la información del usuario actual"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at
    )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Cerrar sesión del usuario"""
    try:
        # En una implementación real, aquí invalidarías el token
        # Por ahora, solo retornamos éxito
        return {"message": "Sesión cerrada exitosamente"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cerrar sesión"
        )

@router.put("/me", response_model=UserResponse)
async def update_user_info(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza la información del usuario actual"""
    try:
        # Validar email si se proporciona
        if user_data.email and user_data.email != current_user.email:
            # Verificar si el email ya está en uso
            existing_user = get_user_by_email(db, user_data.email)
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está registrado"
                )
            
            # Validar formato de email
            if not re.match(r"[^@]+@[^@]+\.[^@]+", user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de email inválido"
                )
        
        # Actualizar campos del usuario
        if user_data.full_name is not None:
            current_user.full_name = user_data.full_name
        if user_data.email is not None:
            current_user.email = user_data.email
        
        db.commit()
        db.refresh(current_user)
        
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            created_at=current_user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/change-password")
async def change_password(
    password_data: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cambia la contraseña del usuario actual"""
    try:
        # Verificar contraseña actual
        if not authenticate_user(db, current_user.email, password_data.current_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta"
            )
        
        # Validar nueva contraseña
        if len(password_data.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña debe tener al menos 6 caracteres"
            )
        
        # Actualizar contraseña
        success = update_user_password(db, current_user.id, password_data.new_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar la contraseña"
            )
        
        return {"message": "Contraseña cambiada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Elimina la cuenta del usuario actual"""
    try:
        # Desactivar usuario en lugar de eliminarlo
        current_user.is_active = False
        db.commit()
        
        return {"message": "Cuenta eliminada exitosamente"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
