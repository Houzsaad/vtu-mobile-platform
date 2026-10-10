# VTU App

A data/airtime VTU (Virtual Top-Up) platform — Django REST API backend, React frontend, with PWA support planned.

> 🚧 **Status: Early development.** Registration is the first complete feature (API + UI + styling, tested end to end). Everything else is in progress or planned.

## Structure

```
vtu-app/
├── backend/      # Django REST API — see backend/README.md
├── frontend/     # React (Vite) frontend — see frontend/README.md
└── docs/         # planning notes, API contracts
```

- **Backend details, setup, and API docs:** [`backend/README.md`](./backend/README.md)
- **Frontend details and setup:** [`frontend/README.md`](./frontend/README.md)

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Django, Django REST Framework |
| Frontend | React (Vite) |
| Database | SQLite (dev) → PostgreSQL (production) |
| API Docs | drf-spectacular (Swagger/Redoc) |
| Deployment | Render |
| Email/OTP | Resend |

## Quick Start

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Backend runs at `http://127.0.0.1:8000`, frontend at `http://localhost:5173`.

## Build Approach

Each feature follows this flow before moving to the next:

1. Build the Django API endpoint → test it
2. Build the React UI → test integration
3. Add styling → test again

One feature at a time — no rushing.

## Progress

- [x] Project structure
- [x] Accounts: Register (API + UI + styling, tested)
- [x] Accounts: Login
- [x] Accounts: Logout
- [x] Accounts: Change Password
- [x] Accounts: Profile
- [ ] Accounts: Forgot Password
- [ ] Wallet
- [ ] Wallet funding
- [ ] Transactions
- [ ] Buy Airtime
- [ ] Buy Data
- [ ] PWA setup

## Author

**Huzaifa Sa'ad** ([@Houzsaad](https://github.com/Houzsaad))
