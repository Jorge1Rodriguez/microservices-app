from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, List
import json
import os
from datetime import datetime

app = FastAPI(title="Orders Microservice")

# Modelo de datos para órdenes
class ProductItem(BaseModel):
    id: Optional[int] = None
    name: str
    price: float
    quantity: int

class OrderBase(BaseModel):
    products: List[dict]
    total_amount: float
    status: str = "pending"

class OrderCreate(OrderBase):
    user_id: int

class OrderResponse(OrderBase):
    id: int
    user_id: int
    created_at: str

# Base de datos simulada (archivo JSON)
DB_FILE = "orders_db.json"

# Inicializar la base de datos si no existe
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

# Funciones de acceso a la base de datos
def read_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def write_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_next_id():
    db = read_db()
    if not db["orders"]:
        return 1
    return max(order["id"] for order in db["orders"]) + 1

# Rutas API
@app.get("/api/orders", response_model=List[OrderResponse])
async def get_orders(x_user_id: Optional[str] = Header(None)):
    db = read_db()
    # Si hay un ID de usuario, filtrar las órdenes por ese usuario
    if x_user_id:
        return [order for order in db["orders"] if order["user_id"] == int(x_user_id)]
    return db["orders"]

@app.get("/api/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, x_user_id: Optional[str] = Header(None)):
    db = read_db()
    for order in db["orders"]:
        if order["id"] == order_id:
            # Verificar si el usuario tiene acceso a esta orden
            if x_user_id and order["user_id"] != int(x_user_id):
                raise HTTPException(status_code=403, detail="Access denied")
            return order
    raise HTTPException(status_code=404, detail="Order not found")

@app.post("/api/orders", response_model=OrderResponse, status_code=201)
async def create_order(order: OrderCreate, x_user_id: Optional[str] = Header(None)):
    # Verificar que el usuario que crea la orden es el mismo que el de la orden
    if x_user_id and order.user_id != int(x_user_id):
        raise HTTPException(status_code=403, detail="Cannot create order for another user")
    
    db = read_db()
    
    # Crear nueva orden
    new_order = order.dict()
    new_order["id"] = get_next_id()
    new_order["created_at"] = datetime.now().isoformat()
    
    db["orders"].append(new_order)
    write_db(db)
    
    return new_order

@app.put("/api/orders/{order_id}", response_model=OrderResponse)
async def update_order(order_id: int, order_data: OrderBase, x_user_id: Optional[str] = Header(None)):
    db = read_db()
    for i, order in enumerate(db["orders"]):
        if order["id"] == order_id:
            # Verificar si el usuario tiene acceso a esta orden
            if x_user_id and order["user_id"] != int(x_user_id):
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Actualizar orden
            db["orders"][i]["products"] = order_data.products
            db["orders"][i]["total_amount"] = order_data.total_amount
            db["orders"][i]["status"] = order_data.status
            
            write_db(db)
            return db["orders"][i]
    raise HTTPException(status_code=404, detail="Order not found")

@app.delete("/api/orders/{order_id}")
async def delete_order(order_id: int, x_user_id: Optional[str] = Header(None)):
    db = read_db()
    for i, order in enumerate(db["orders"]):
        if order["id"] == order_id:
            # Verificar si el usuario tiene acceso a esta orden
            if x_user_id and order["user_id"] != int(x_user_id):
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Eliminar orden
            del db["orders"][i]
            write_db(db)
            return {"message": "Order deleted successfully"}
    raise HTTPException(status_code=404, detail="Order not found")
