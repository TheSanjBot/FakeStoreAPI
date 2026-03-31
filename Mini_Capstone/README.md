# Mini Capstone

This project is now split into two folders:

- `backend` for the FastAPI and MongoDB API
- `frontend` for the simple React user interface

## Project structure

```text
Mini_Capstone/
├── backend/
└── frontend/
```

## Backend setup

1. Open PowerShell
2. Go to the backend folder:

```powershell
cd "c:\Users\Sanjay H\OneDrive\Desktop\Mini_Capstone\backend"
```

3. Activate the backend virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

4. Start the backend:

```powershell
python -m uvicorn app.main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

## Frontend setup

1. Open a second PowerShell window
2. Go to the frontend folder:

```powershell
cd "c:\Users\Sanjay H\OneDrive\Desktop\Mini_Capstone\frontend"
```

3. Install frontend packages:

```powershell
cmd /c npm install
```

4. Start the React app:

```powershell
cmd /c npm run dev
```

The frontend will run at:

```text
http://127.0.0.1:5173
```

## Default backend login

Use this admin login first:

- Email: `admin@logisticsapp.com`
- Password: `Admin@123`

## How to test the final project

1. Start the backend
2. Start the frontend
3. Open `http://127.0.0.1:5173`
4. Log in with the admin account
5. Check that the admin dashboard loads users, reports, agents, and shipments
6. Register a customer account
7. Register an agent account
8. Log in as the customer and create a shipment
9. Log back in as the admin and assign the shipment to the agent
10. Log in as the agent and update the shipment status


**What To Keep Running**

You need both servers running.

Backend:
```powershell
cd "C:\Users\Sanjay H\OneDrive\Desktop\Mini_Capstone\backend"
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Frontend:
```powershell
cd "C:\Users\Sanjay H\OneDrive\Desktop\Mini_Capstone\frontend"
cmd /c npm run dev
```

Open:
- UI: `http://127.0.0.1:5173`
- Swagger: `http://127.0.0.1:8000/docs`

Your database is on MongoDB Atlas, so if backend starts without Atlas errors, cloud connection is working.

**1. Test In Swagger**

Open `http://127.0.0.1:8000/docs`

First test:
- `GET /health`
- Click `Try it out`
- Click `Execute`
- Expected:
```json
{"status":"ok"}
```

Admin login:
- Open `POST /api/v1/auth/login`
- Use:
```json
{
  "email": "admin@logisticsapp.com",
  "password": "Admin@123"
}
```
- Execute
- Copy `access_token`

Authorize:
- Click `Authorize` at top right
- Paste only the token
- Click `Authorize`
- Click `Close`

Now test admin routes:
- `GET /api/v1/auth/me`
Expected: admin profile
- `GET /api/v1/admin/users`
Expected: list of users
- `GET /api/v1/admin/reports`
Expected: user and shipment counts

Register test users:
- `POST /api/v1/auth/register`
Customer:
```json
{
  "name": "Customer One",
  "email": "customer1@example.com",
  "password": "Customer@123",
  "role": "customer"
}
```
Agent:
```json
{
  "name": "Agent One",
  "email": "agent1@example.com",
  "password": "Agent@123",
  "role": "agent"
}
```

Then:
- Login as customer
- Copy customer token
- Authorize with customer token
- `POST /api/v1/shipments`
```json
{
  "source_address": "Chennai",
  "destination_address": "Bangalore"
}
```
- Copy returned `id` and `tracking_number`

Then:
- Login as admin again
- Authorize with admin token
- `GET /api/v1/users/agents`
- Copy agent `id`
- `PUT /api/v1/shipments/{shipment_id}/assign-agent`
```json
{
  "agent_id": "PASTE_AGENT_ID"
}
```

Then:
- Login as agent
- Authorize with agent token
- `PUT /api/v1/shipments/{shipment_id}/status`
```json
{
  "status": "in_transit",
  "location": "Salem Hub",
  "note": "Shipment received at hub"
}
```

Finally:
- Login as customer again
- Authorize with customer token
- `GET /api/v1/shipments/{tracking_number}`
Expected: tracking timeline with the update

**2. Test In The UI**

Open `http://127.0.0.1:5173`

Admin flow:
1. Log in with:
- Email: `admin@logisticsapp.com`
- Password: `Admin@123`
2. Confirm the page shows:
- Reports
- All users
- All shipments
- Assign Agent form

Create users:
1. Logout
2. Register a customer
3. Register an agent

Customer flow:
1. Log in as the customer
2. Fill `Create Shipment`
3. Submit
4. Confirm it appears in `My Shipments`
5. Copy the tracking number from the table

Admin flow again:
1. Logout
2. Log in as admin
3. In `Assign Agent`, paste the shipment ID
4. Choose the agent from dropdown
5. Click `Assign`

Agent flow:
1. Logout
2. Log in as the agent
3. Confirm assigned shipment appears
4. In `Update Status`, paste shipment ID
5. Choose status
6. Enter location and note
7. Save update

Customer tracking flow:
1. Logout
2. Log in as customer
3. In `Track Shipment`, paste tracking number
4. Click `Track`
5. Confirm status and tracking history appear

**3. Test Atlas Cloud**

This is how to confirm MongoDB Atlas is actually storing data.

Option 1: easiest
- Open MongoDB Atlas
- Go to your cluster
- Open `Browse Collections` or `Collections`
- Open database `logistics_db`
- Check these collections:
  - `users`
  - `shipments`
  - `tracking_updates`
  - `hubs`

What you should see:
- your admin, customer, and agent in `users`
- created shipment in `shipments`
- status updates in `tracking_updates`

Option 2: strongest proof
1. Create a new customer or shipment in the UI
2. Refresh Atlas collection view
3. Confirm the new document appears there

That proves:
- frontend -> backend works
- backend -> Atlas works
- Atlas is persisting the data

**Minimum Full Test**

If you want the shortest complete test, do this:

1. Start backend
2. Start frontend
3. Swagger `GET /health`
4. UI admin login
5. UI register customer
6. UI register agent
7. UI customer creates shipment
8. UI admin assigns agent
9. UI agent updates status
10. UI customer tracks shipment
11. Atlas shows all created data

**If Something Fails**

- `401`: wrong or missing token
- `403`: wrong role for that route
- `422`: invalid request body
- backend not starting: Atlas URI or `.env` issue
- UI not loading data: backend may not be running on `127.0.0.1:8000`

If you want, I can give you the exact testing sequence as:
1. Swagger-only
2. UI-only
3. Atlas-only
with no extra explanation, just clicks and payloads.
11. Log back in as the customer and track the shipment using the tracking number

## Notes

- The frontend is intentionally simple and basic
- It uses plain React state, plain CSS, and direct `fetch` calls
- The backend still uses your Atlas MongoDB connection through `backend/.env`
- The backend reads `backend/.env`, not any `.env` file inside `.venv`
