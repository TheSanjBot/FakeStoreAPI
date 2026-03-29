# Logistics API

Backend-only implementation of the logistics and shipment tracking system from your PDF. This version focuses on OOP structure, FastAPI, MongoDB, JWT auth, RBAC, and the core customer, agent, and admin flows.

## What is included

- FastAPI backend with layered architecture: controllers, services, repositories, models, and schemas
- MongoDB integration with collection indexes
- JWT-based authentication and role-based authorization
- Shipment creation, tracking, assignment, status updates, hub management, admin reports, and user management
- Docker support for the API plus MongoDB

## Folder to use

Work from:

```powershell
cd "c:\Users\Sanjay H\OneDrive\Desktop\Mini_Capstone\logistics-api"
```

## Run locally

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create your environment file:

```powershell
Copy-Item .env.example .env
```

4. Make sure MongoDB is running on `mongodb://localhost:27017`.

If you do not already have MongoDB running, you can start it with Docker:

```powershell
docker compose up -d mongo
```

5. Start the API:

```powershell
uvicorn app.main:app --reload
```

6. Open the docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Use MongoDB Atlas instead of local MongoDB

1. Create a free Atlas project and cluster.
2. Create a database user inside Atlas.
3. Add your current IP address in Atlas Network Access.
4. In Atlas, click `Connect` on the cluster, choose `Drivers`, and copy the Python connection string.
5. Replace the `MONGO_URI` value in `.env` with that Atlas URI.
6. Replace `<db_password>` in the URI with your actual database user password.
7. Start the API with `uvicorn app.main:app --reload`.

Example:

```env
MONGO_URI=mongodb+srv://myuser:myPassword123@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGO_DB=logistics_db
```

If your password contains special characters such as `@`, `:`, `/`, or `#`, URL-encode it before placing it in the URI.

## Run with Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```

The API will be available at `http://127.0.0.1:8000`.

## Default admin account

On first startup, the app seeds one admin user if it does not already exist:

- Email: `admin@logisticsapp.com`
- Password: `Admin@123`

Change these values in `.env` before using the project seriously.

## Registration behavior

Public registration is intentionally limited to:

- `customer`
- `agent`

`admin` is seeded from environment variables for safety.

## Useful routes

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/shipments`
- `GET /api/v1/shipments`
- `GET /api/v1/shipments/{tracking_number}`
- `DELETE /api/v1/shipments/{shipment_id}`
- `PUT /api/v1/shipments/{shipment_id}/assign-agent`
- `PUT /api/v1/shipments/{shipment_id}/status`
- `POST /api/v1/tracking/{shipment_id}`
- `GET /api/v1/agent/shipments`
- `GET /api/v1/users/agents`
- `POST /api/v1/admin/hubs`
- `GET /api/v1/admin/hubs`
- `PUT /api/v1/admin/hubs/{hub_id}`
- `DELETE /api/v1/admin/hubs/{hub_id}`
- `GET /api/v1/admin/reports`
- `GET /api/v1/admin/users`
- `DELETE /api/v1/admin/users/{user_id}`

## Optional seed script

To insert a sample customer, agent, and a couple of hubs:

```powershell
python scripts/seed_data.py
```
