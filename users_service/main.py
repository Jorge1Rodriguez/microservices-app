from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import json
import os
from datetime import datetime
from passlib.context import CryptContext

app = FastAPI(title="Users Microservice")

# Configuración para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelo de datos para usuarios
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    role: str = "user"  # Valores posibles: "admin", "user"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: str

class LoginRequest(BaseModel):
    username: str
    password: str

# Base de datos simulada (archivo JSON)
DB_FILE = "users_db.json"

# Inicializar la base de datos si no existe
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({
            "users": [
                {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@example.com",
                    "password": pwd_context.hash("admin123"),
                    "full_name": "Administrator",
                    "role": "admin",  # Administrador
                    "is_active": True,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": 2,
                    "username": "user",
                    "email": "user@example.com",
                    "password": pwd_context.hash("user123"),
                    "full_name": "Regular User",
                    "role": "user",  # Usuario normal
                    "is_active": True,
                    "created_at": datetime.now().isoformat()
                }
            ]
        }, f, indent=4)

# Funciones de acceso a la base de datos
def read_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def write_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_next_id():
    db = read_db()
    if not db["users"]:
        return 1
    return max(user["id"] for user in db["users"]) + 1

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Rutas API
@app.post("/api/login")
async def login(login_data: LoginRequest):
    db = read_db()
    for user in db["users"]:
        if user["username"] == login_data.username and verify_password(login_data.password, user["password"]):
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"]  # Incluir el rol en la respuesta
            }
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.get("/api/users", response_model=List[UserResponse])
async def get_users(x_user_id: Optional[str] = Header(None)):
    db = read_db()
    # Omitir la contraseña en la respuesta
    return [
        {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],  # Incluir el rol
            "is_active": user["is_active"],
            "created_at": user["created_at"]
        } 
        for user in db["users"]
    ]

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, x_user_id: Optional[str] = Header(None)):
    db = read_db()
    for user in db["users"]:
        if user["id"] == user_id:
            # Omitir la contraseña en la respuesta
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],  # Incluir el rol
                "is_active": user["is_active"],
                "created_at": user["created_at"]
            }
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/api/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, x_user_id: Optional[str] = Header(None)):
    db = read_db()
    # Verificar si el nombre de usuario ya existe
    if any(u["username"] == user.username for u in db["users"]):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Crear nuevo usuario
    hashed_password = pwd_context.hash(user.password)
    new_user = {
        "id": get_next_id(),
        "username": user.username,
        "email": user.email,
        "password": hashed_password,
        "full_name": user.full_name,
        "role": user.role,  # Guardar el rol especificado
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    
    db["users"].append(new_user)
    write_db(db)
    
    # Omitir la contraseña en la respuesta
    return {
        "id": new_user["id"],
        "username": new_user["username"],
        "email": new_user["email"],
        "full_name": new_user["full_name"],
        "role": new_user["role"],  # Incluir el rol en la respuesta
        "is_active": new_user["is_active"],
        "created_at": new_user["created_at"]
    }

@app.put("/api/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserBase, x_user_id: Optional[str] = Header(None)):
    db = read_db()
    for i, user in enumerate(db["users"]):
        if user["id"] == user_id:
            # Actualizar usuario
            db["users"][i]["username"] = user_data.username
            db["users"][i]["email"] = user_data.email
            db["users"][i]["full_name"] = user_data.full_name
            db["users"][i]["role"] = user_data.role  # Actualizar el rol
            
            write_db(db)
            
            # Omitir la contraseña en la respuesta
            return {
                "id": db["users"][i]["id"],
                "username": db["users"][i]["username"],
                "email": db["users"][i]["email"],
                "full_name": db["users"][i]["full_name"],
                "role": db["users"][i]["role"],  # Incluir el rol
                "is_active": db["users"][i]["is_active"],
                "created_at": db["users"][i]["created_at"]
            }
    raise HTTPException(status_code=404, detail="User not found")

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int, x_user_id: Optional[str] = Header(None)):
    db = read_db()
    for i, user in enumerate(db["users"]):
        if user["id"] == user_id:
            # Eliminar usuario
            del db["users"][i]
            write_db(db)
            return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")
