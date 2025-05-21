from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import aiohttp
from datetime import timedelta

from auth.jwt_handler import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user

router = APIRouter(prefix="/api")

# URLs de los servicios
USERS_SERVICE_URL = "http://users_service:8001/api"
ORDERS_SERVICE_URL = "http://orders_service:8002/api"

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint para autenticación de usuarios.
    """
    try:
        async with aiohttp.ClientSession() as session:
            # Usar form_data en lugar de JSON para compatibilidad con OAuth2
            form_data_dict = {
                "username": form_data.username,
                "password": form_data.password
            }
            
            async with session.post(
                f"{USERS_SERVICE_URL}/login",
                data=form_data_dict  # Usar data en lugar de json
            ) as response:
                if response.status == 200:
                    user_data = await response.json()
                    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                    access_token = create_access_token(
                        data={"sub": str(user_data["id"])},
                        expires_delta=access_token_expires
                    )
                    return {"access_token": access_token, "token_type": "bearer"}
                
                # Proporcionar más información sobre el error
                error_detail = "Incorrect username or password"
                try:
                    error_json = await response.json()
                    if "detail" in error_json:
                        error_detail = error_json["detail"]
                except:
                    pass
                
                raise HTTPException(status_code=401, detail=error_detail)
    except Exception as e:
        # Manejar excepciones de conexión y otras
        print(f"Error en login: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during authentication")


# Rutas para usuarios
@router.get("/users")
async def get_users(current_user: dict = Depends(get_current_user)):
    """
    Obtiene todos los usuarios.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{USERS_SERVICE_URL}/users",
            headers={"X-User-ID": str(current_user["id"])}
        ) as response:
            if response.status == 200:
                return await response.json()
            raise HTTPException(status_code=response.status, detail="Error fetching users")

@router.get("/users/{user_id}")
async def get_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """
    Obtiene un usuario por su ID.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{USERS_SERVICE_URL}/users/{user_id}",
            headers={"X-User-ID": str(current_user["id"])}
        ) as response:
            if response.status == 200:
                return await response.json()
            raise HTTPException(status_code=response.status, detail="Error fetching user")

@router.post("/users")
async def create_user(user_data: dict, current_user: dict = Depends(get_current_user)):
    """
    Crea un nuevo usuario.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{USERS_SERVICE_URL}/users",
            json=user_data,
            headers={"X-User-ID": str(current_user["id"])}
        ) as response:
            if response.status == 201:
                return await response.json()
            raise HTTPException(status_code=response.status, detail="Error creating user")

@router.put("/users/{user_id}")
async def update_user(user_id: int, user_data: dict, current_user: dict = Depends(get_current_user)):
    """
    Actualiza un usuario existente.
    """
    async with aiohttp.ClientSession() as session:
        async with session.put(
            f"{USERS_SERVICE_URL}/users/{user_id}",
            json=user_data,
            headers={"X-User-ID": str(current_user["id"])}
        ) as response:
            if response.status == 200:
                return await response.json()
            raise HTTPException(status_code=response.status, detail="Error updating user")

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """
    Elimina un usuario.
    """
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"{USERS_SERVICE_URL}/users/{user_id}",
            headers={"X-User-ID": str(current_user["id"])}
        ) as response:
            if response.status == 200:
                return await response.json()
            raise HTTPException(status_code=response.status, detail="Error deleting user")

# Rutas para órdenes
@router.get("/orders")
async def get_orders(current_user: dict = Depends(get_current_user)):
    """
    Obtiene todas las órdenes del usuario actual.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{ORDERS_SERVICE_URL}/orders",
            headers={"X-User-ID": str(current_user["id"])}
        ) as response:
            if response.status == 200:
                return await response.json()
            raise HTTPException(status_code=response.status, detail="Error fetching orders")

@router.get("/orders/{order_id}")
async def get_order(order_id: int, current_user: dict = Depends(get_current_user)):
    """
    Obtiene una orden por su ID.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{ORDERS_SERVICE_URL}/orders/{order_id}",
            headers={"X-User-ID": str(current_user["id"])}
        ) as response:
            if response.status == 200:
                return await response.json()
            raise HTTPException(status_code=response.status, detail="Error fetching order")

@router.post("/orders")
async def create_order(order_data: dict, current_user: dict = Depends(get_current_user)):
    """
    Crea una nueva orden.
    """
    # Añadir el ID del usuario a los datos de la orden
    order_data["user_id"] = int(current_user["id"])
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{ORDERS_SERVICE_URL}/orders",
            json=order_data,
            headers={"X-User-ID": str(current_user["id"])}
        ) as response:
            if response.status == 201:
                return await response.json()
            raise HTTPException(status_code=response.status, detail="Error creating order")

@router.put("/orders/{order_id}")
async def update_order(order_id: int, order_data: dict, current_user: dict = Depends(get_current_user)):
    """
    Actualiza una orden existente.
    """
    async with aiohttp.ClientSession() as session:
        async with session.put(
            f"{ORDERS_SERVICE_URL}/orders/{order_id}",
            json=order_data,
            headers={"X-User-ID": str(current_user["id"])}
        ) as response:
            if response.status == 200:
                return await response.json()
            raise HTTPException(status_code=response.status, detail="Error updating order")

@router.delete("/orders/{order_id}")
async def delete_order(order_id: int, current_user: dict = Depends(get_current_user)):
    """
    Elimina una orden.
    """
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"{ORDERS_SERVICE_URL}/orders/{order_id}",
            headers={"X-User-ID": str(current_user["id"])}
        ) as response:
            if response.status == 200:
                return await response.json()
            raise HTTPException(status_code=response.status, detail="Error deleting order")
