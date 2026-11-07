# VTU App

A VTU (airtime and data) platform: a Django REST API backend and a React (Vite) frontend that installs as a PWA. Users fund a wallet by bank transfer and buy airtime and data with a transaction PIN. Admins manage plans, prices, pending transactions and announcements from the Django admin.

## Live demo

| Part | Link |
|------|------|
| Frontend | https://vtu-mobile-platform.vercel.app |
| Backend API docs | https://vtu-mobile-platform.onrender.com/api/docs/ |

> **Note:** The demo backend runs on Render's free tier, so the first request after a period of inactivity can take up to a minute. Free hosting also has monthly usage limits, so the demo may occasionally be unavailable.

## What it does

- **Accounts:** register, login, logout, profile, change password, change transaction PIN, forgot password (one-time code by email)
- **Wallet:** one wallet per user, with a ledger that records every money movement
- **Funding:** bank transfer to a temporary account (Paystack Pay with Transfer), credited automatically through a signed webhook
- **Purchases:** airtime and data with PIN confirmation; data plans are grouped by network and plan type
- **History:** every transaction with a status of Successful, Pending, Failed or Refunded
- **Admin tools:** settle pending transactions, set plan prices, activate plans, review funding requests, post announcements
- **PWA:** installable and works like a mobile app

## How money is kept safe

- A wallet is credited only by a verified payment webhook, and the same payment can never credit twice.
- A purchase locks the wallet, debits first, and never holds a database lock while calling the provider.
- Only an explicit provider success counts as success, and only an explicit failure is refunded, exactly once.
- Anything unclear stays **pending** for manual review in the admin.

Details are in [`backend/README.md`](./backend/README.md).

## Structure

```
vtu-mobile-platform/
├── backend/      # Django REST API: see backend/README.md
├── frontend/     # React (Vite) PWA: see frontend/README.md
└── docs/         # planning notes, API contracts
```

- **Backend setup, environment variables, deployment and admin guide:** [`backend/README.md`](./backend/README.md)
- **Frontend setup and screens:** [`frontend/README.md`](./frontend/README.md)

## Tech stack

| Layer | Tech |
|---|---|
| Backend | Django, Django REST Framework, Simple JWT |
| Frontend | React (Vite), react-router-dom, vite-plugin-pwa |
| Database | PostgreSQL (Neon) |
| Providers | DodoData (default), VTPass |
| Payments | Paystack (Pay with Transfer) |
| Email | Resend (needs a verified domain) |
| API docs | drf-spectacular (Swagger / Redoc) |
| Deployment | Render (API), Vercel (frontend) |

## Quick start

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

The frontend needs a `frontend/.env` file with `VITE_API_URL=http://127.0.0.1:8000/api`, and the backend needs a `backend/.env` file. The variables are listed in each folder's README. Never commit `.env` files.

The backend runs at `http://127.0.0.1:8000` and the frontend at `http://localhost:5173`.

## Progress

- [x] Accounts: register, login, logout, profile
- [x] Accounts: change password and change transaction PIN
- [x] Accounts: forgot password
- [x] Wallet and transaction ledger
- [x] Transaction history
- [x] Buy airtime
- [x] Buy data (network, plan type, plan)
- [x] Wallet funding (bank transfer)
- [x] Admin tools and announcements
- [x] PWA setup
- [ ] Real email delivery (needs a verified domain)
- [ ] Rate limit on login and registration

## Build approach

Each feature followed the same flow before the next one started:

1. Build the Django API endpoint and test it
2. Build the React UI and test the integration
3. Add styling and test again

## Author

**Huzaifa Sa'ad** ([@Houzsaad](https://github.com/Houzsaad))
