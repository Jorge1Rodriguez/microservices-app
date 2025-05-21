import json
import os
from datetime import datetime
from passlib.context import CryptContext

# Configuración para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Ruta del archivo de base de datos
DB_FILE = "users_db.json"

def initialize_db():
    """
    Inicializa la base de datos si no existe.
    """
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({
                "users": [
                    {
                        "id": 1,
                        "username": "admin",
                        "email": "admin@example.com",
                        "hashed_password": pwd_context.hash("admin123"),
                        "full_name": "Administrator",
                        "is_active": True,
                        "created_at": datetime.now().isoformat()
                    },
                    {
                        "id": 2,
                        "username": "user",
                        "email": "user@example.com",
                        "hashed_password": pwd_context.hash("user123"),
                        "full_name": "Regular User",
                        "is_active": True,
                        "created_at": datetime.now().isoformat()
                    }
                ]
            }, f, indent=4)

def read_db():
    """
    Lee la base de datos.
    """
    initialize_db()
    with open(DB_FILE, "r") as f:
        return json.load(f)

def write_db(data):
    """
    Escribe en la base de datos.
    """
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_next_id():
    """
    Obtiene el siguiente ID disponible.
    """
    db = read_db()
    if not db["users"]:
        return 1
    return max(user["id"] for user in db["users"]) + 1

def verify_password(plain_password, hashed_password):
    """
    Verifica si la contraseña es correcta.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Genera un hash para la contraseña.
    """
    return pwd_context.hash(password)
