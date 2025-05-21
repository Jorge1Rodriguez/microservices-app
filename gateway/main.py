from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import aiohttp
from datetime import timedelta
import os

from auth.jwt_handler import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from auth.role_checker import RoleChecker

app = FastAPI(title="Microservices API Gateway")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar plantillas
templates = Jinja2Templates(directory="templates")

# Configuración de servicios
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://users_service:8001/api")
ORDERS_SERVICE_URL = os.getenv("ORDERS_SERVICE_URL", "http://orders_service:8002/api")

# Definir verificadores de roles
admin_only = RoleChecker(["admin"])
any_user = RoleChecker(["admin", "user"])

# Rutas para la interfaz de usuario
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "app_name": "Microservices App"})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/users", response_class=HTMLResponse)
async def users_page(request: Request):
    return templates.TemplateResponse("users.html", {"request": request})

@app.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request):
    return templates.TemplateResponse("orders.html", {"request": request})

# API para autenticación
@app.post("/api/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint para autenticación de usuarios.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{USERS_SERVICE_URL}/login",
                json={"username": form_data.username, "password": form_data.password}
            ) as response:
                if response.status == 200:
                    user_data = await response.json()
                    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                    access_token = create_access_token(
                        data={
                            "sub": str(user_data["id"]),
                            "role": user_data.get("role", "user")  # Incluir el rol en el token
                        },
                        expires_delta=access_token_expires
                    )
                    return {"access_token": access_token, "token_type": "bearer"}
                
                error_detail = "Incorrect username or password"
                try:
                    error_json = await response.json()
                    if "detail" in error_json:
                        error_detail = error_json["detail"]
                except:
                    pass
                
                raise HTTPException(status_code=401, detail=error_detail)
    except Exception as e:
        print(f"Error en login: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# API Gateway para el servicio de usuarios
@app.get("/api/users")
async def get_users(current_user: dict = Depends(get_current_user)):
    """
    Obtiene todos los usuarios.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{USERS_SERVICE_URL}/users",
                headers={"X-User-ID": str(current_user["id"])}
            ) as response:
                if response.status == 200:
                    return await response.json()
                raise HTTPException(status_code=response.status, detail="Error fetching users")
    except Exception as e:
        print(f"Error en get_users: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Ruta protegida solo para administradores
@app.get("/api/admin/users", dependencies=[Depends(admin_only)])
async def get_all_users():
    """
    Endpoint solo para administradores para obtener todos los usuarios.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{USERS_SERVICE_URL}/users"
            ) as response:
                if response.status == 200:
                    return await response.json()
                raise HTTPException(status_code=response.status, detail="Error fetching users")
    except Exception as e:
        print(f"Error en get_all_users: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/users/{user_id}")
async def get_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """
    Obtiene un usuario por su ID.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{USERS_SERVICE_URL}/users/{user_id}",
                headers={"X-User-ID": str(current_user["id"])}
            ) as response:
                if response.status == 200:
                    return await response.json()
                raise HTTPException(status_code=response.status, detail="Error fetching user")
    except Exception as e:
        print(f"Error en get_user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/users")
async def create_user(user_data: dict, current_user: dict = Depends(get_current_user)):
    """
    Crea un nuevo usuario.
    """
    # Solo los administradores pueden crear otros administradores
    if user_data.get("role") == "admin" and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo los administradores pueden crear usuarios administradores"
        )
        
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{USERS_SERVICE_URL}/users",
                json=user_data,
                headers={"X-User-ID": str(current_user["id"])}
            ) as response:
                if response.status == 201:
                    return await response.json()
                raise HTTPException(status_code=response.status, detail="Error creating user")
    except Exception as e:
        print(f"Error en create_user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/api/users/{user_id}")
async def update_user(user_id: int, user_data: dict, current_user: dict = Depends(get_current_user)):
    """
    Actualiza un usuario existente.
    """
    # Solo los administradores pueden cambiar roles o modificar otros administradores
    if current_user.get("role") != "admin":
        # Verificar si se está intentando cambiar el rol
        if "role" in user_data and user_data["role"] == "admin":
            raise HTTPException(
                status_code=403,
                detail="Solo los administradores pueden asignar el rol de administrador"
            )
            
        # Verificar si se está intentando modificar un administrador
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{USERS_SERVICE_URL}/users/{user_id}"
                ) as response:
                    if response.status == 200:
                        target_user = await response.json()
                        if target_user.get("role") == "admin" and str(current_user["id"]) != str(user_id):
                            raise HTTPException(
                                status_code=403,
                                detail="No tienes permisos para modificar un usuario administrador"
                            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error al verificar permisos: {str(e)}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{USERS_SERVICE_URL}/users/{user_id}",
                json=user_data,
                headers={"X-User-ID": str(current_user["id"])}
            ) as response:
                if response.status == 200:
                    return await response.json()
                raise HTTPException(status_code=response.status, detail="Error updating user")
    except Exception as e:
        print(f"Error en update_user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """
    Elimina un usuario.
    """
    # Solo los administradores pueden eliminar usuarios (excepto a sí mismos)
    if current_user.get("role") != "admin" and str(current_user["id"]) != str(user_id):
        raise HTTPException(
            status_code=403,
            detail="Solo los administradores pueden eliminar otros usuarios"
        )
        
    # Verificar si se está intentando eliminar un administrador siendo un usuario normal
    if current_user.get("role") != "admin":
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{USERS_SERVICE_URL}/users/{user_id}"
                ) as response:
                    if response.status == 200:
                        target_user = await response.json()
                        if target_user.get("role") == "admin":
                            raise HTTPException(
                                status_code=403,
                                detail="No tienes permisos para eliminar un usuario administrador"
                            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error al verificar permisos: {str(e)}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{USERS_SERVICE_URL}/users/{user_id}",
                headers={"X-User-ID": str(current_user["id"])}
            ) as response:
                if response.status == 200:
                    return await response.json()
                raise HTTPException(status_code=response.status, detail="Error deleting user")
    except Exception as e:
        print(f"Error en delete_user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# API Gateway para el servicio de órdenes
@app.get("/api/orders")
async def get_orders(current_user: dict = Depends(get_current_user)):
    """
    Obtiene todas las órdenes del usuario actual.
    """
    try:
        async with aiohttp.ClientSession() as session:
            # Si es admin, puede ver todas las órdenes, si no, solo las suyas
            if current_user.get("role") == "admin":
                async with session.get(
                    f"{ORDERS_SERVICE_URL}/orders"
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    raise HTTPException(status_code=response.status, detail="Error fetching orders")
            else:
                async with session.get(
                    f"{ORDERS_SERVICE_URL}/orders",
                    headers={"X-User-ID": str(current_user["id"])}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    raise HTTPException(status_code=response.status, detail="Error fetching orders")
    except Exception as e:
        print(f"Error en get_orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/orders/{order_id}")
async def get_order(order_id: int, current_user: dict = Depends(get_current_user)):
    """
    Obtiene una orden por su ID.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ORDERS_SERVICE_URL}/orders/{order_id}",
                headers={"X-User-ID": str(current_user["id"])}
            ) as response:
                if response.status == 200:
                    return await response.json()
                raise HTTPException(status_code=response.status, detail="Error fetching order")
    except Exception as e:
        print(f"Error en get_order: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/orders")
async def create_order(order_data: dict, current_user: dict = Depends(get_current_user)):
    """
    Crea una nueva orden.
    """
    try:
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
    except Exception as e:
        print(f"Error en create_order: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/api/orders/{order_id}")
async def update_order(order_id: int, order_data: dict, current_user: dict = Depends(get_current_user)):
    """
    Actualiza una orden existente.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{ORDERS_SERVICE_URL}/orders/{order_id}",
                json=order_data,
                headers={"X-User-ID": str(current_user["id"])}
            ) as response:
                if response.status == 200:
                    return await response.json()
                raise HTTPException(status_code=response.status, detail="Error updating order")
    except Exception as e:
        print(f"Error en update_order: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/api/orders/{order_id}")
async def delete_order(order_id: int, current_user: dict = Depends(get_current_user)):
    """
    Elimina una orden.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{ORDERS_SERVICE_URL}/orders/{order_id}",
                headers={"X-User-ID": str(current_user["id"])}
            ) as response:
                if response.status == 200:
                    return await response.json()
                raise HTTPException(status_code=response.status, detail="Error deleting order")
    except Exception as e:
        print(f"Error en delete_order: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
