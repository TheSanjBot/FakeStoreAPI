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
11. Log back in as the customer and track the shipment using the tracking number

## Notes

- The frontend is intentionally simple and basic
- It uses plain React state, plain CSS, and direct `fetch` calls
- The backend still uses your Atlas MongoDB connection through `backend/.env`
- The backend reads `backend/.env`, not any `.env` file inside `.venv`
