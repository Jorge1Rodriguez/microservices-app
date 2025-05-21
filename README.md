# Microservices Application with FastAPI

Esta aplicación implementa una arquitectura de microservicios utilizando FastAPI, con autenticación JWT y configuración para DevOps (Docker y CI/CD con GitHub Actions).

## Estructura del Proyecto

- `gateway`: API Gateway que maneja la autenticación y enruta las peticiones a los microservicios internos
- `users_service`: Servicio para la gestión de usuarios
- `orders_service`: Servicio para la gestión de órdenes
- `tests`: Pruebas automatizadas para los servicios

## Características

- **API REST completa**: Implementa métodos POST, GET, PUT y DELETE
- **Autenticación JWT**: Protege los endpoints con JSON Web Tokens
- **Microservicios**: Arquitectura basada en microservicios independientes
- **Interfaz de Usuario**: Frontend con HTML y CSS para interactuar con los servicios
- **DevOps**: Configuración para Docker y CI/CD con GitHub Actions

## Requisitos

- Python 3.9+
- Docker y Docker Compose

## Ejecución

### Con Docker Compose

docker-compose up --build


La aplicación estará disponible en:
- Gateway: http://localhost:8000
- Documentación API: http://localhost:8000/docs

### Desarrollo Local

1. Instalar dependencias para cada servicio:


1. Instalar dependencias para cada servicio:

cd gateway && pip install -r requirements.txt
cd users_service && pip install -r requirements.txt
cd orders_service && pip install -r requirements.txt


2. Ejecutar cada servicio en una terminal separada:

cd gateway && uvicorn main:app --reload --port 8000
cd users_service && uvicorn main:app --reload --port 8001
cd orders_service && uvicorn main:app --reload --port 8002



## Pruebas

Para ejecutar las pruebas:

pytest

text

## CI/CD

El proyecto incluye configuración para CI/CD con GitHub Actions. Cada push a las ramas main o master desencadenará:
1. Ejecución de pruebas
2. Construcción de imágenes Docker
3. Publicación de imágenes en Docker Hub

## Usuarios Predeterminados

- Admin: username=admin, password=admin123
- Usuario: username=user, password=user123
