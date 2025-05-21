import json
import os
from datetime import datetime

# Ruta del archivo de base de datos
DB_FILE = "orders_db.json"

def initialize_db():
    """
    Inicializa la base de datos si no existe.
    """
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({
                "orders": [
                    {
                        "id": 1,
                        "user_id": 1,
                        "products": [
                            {"id": 1, "name": "Product 1", "price": 10.99, "quantity": 2}
                        ],
                        "total_amount": 21.98,
                        "status": "completed",
                        "created_at": datetime.now().isoformat()
                    },
                    {
                        "id": 2,
                        "user_id": 2,
                        "products": [
                            {"id": 2, "name": "Product 2", "price": 15.99, "quantity": 1}
                        ],
                        "total_amount": 15.99,
                        "status": "pending",
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
    if not db["orders"]:
        return 1
    return max(order["id"] for order in db["orders"]) + 1
