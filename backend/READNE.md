VTU App

A data/airtime VTU (Virtual Top-Up) platform built with Django (backend API) and React (frontend), with PWA support planned for installable, offline-friendly access.

🚧 Status: Early development. The accounts system (registration) is the first working piece. Most features below are planned, not yet built.

Tech Stack
Backend: Django, Django REST Framework
Frontend: React (with PWA features)
Database: SQLite (development) → PostgreSQL (production)
API Docs: drf-spectacular (Swagger/Redoc)
Deployment: Render
Email/OTP: Resend

Project Structure
vtu-app/
├── backend/
│   ├── config/          # Django project settings, root URLs
│   ├── accounts/        # User registration, auth, profile
│   ├── wallet/          # User wallet (created automatically on registration)
│   └── manage.py
├── frontend/            # React app (PWA)
└── docs/                # API contracts, planning notes

Features
✅ Done
Project structure (Django backend + React frontend planned)
Custom User model (full name, unique username, unique email, phone number)
Registration endpoint (POST /api/accounts/register/)
Phone number validation (11 digits, must start with 090/091/080/081/070)
Password validation (must include uppercase, lowercase, number, special character, min 8 chars)
Transaction PIN (4 digits, numeric only, stored hashed, separate from login password)
Full name/username restricted to letters (+ apostrophes for names), no special characters
Automatic wallet creation on registration (via signal)

🚧 Planned
 Login (username + password, JWT-based)
 Logout
 Forgot Password (OTP via Resend, reset flow)
 Change Password
 Forgot PIN
 User Profile endpoint
 Wallet funding (payment provider integration)
 Transaction history
 Airtime purchase
 Data purchase
 Rate limiting on sensitive endpoints
 React frontend (registration, login, dashboard)
 PWA setup (installable, offline caching)

Account Rules

Phone number: 11 digits, numbers only, must start with 090, 091, 080, 081, or 070.

Password: minimum 8 characters, must contain at least one lowercase letter, one uppercase letter, one number, and one special character.

Transaction PIN: exactly 4 digits, numeric only, stored separately (hashed) from the login password.

Full name: letters, spaces, and apostrophes only (e.g. Sani, Sa'ad, John). No numbers or symbols.

Username: letters and numbers only. Must be unique.

Local Setup (Backend)
bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py runserver

API will be available at http://127.0.0.1:8000/.

API Documentation

Once the server is running:

Swagger UI: /api/docs/
Redoc: /api/redoc/
Raw schema: /api/schema/

Environment Variables
Copy .env.example to .env and fill in real values (never commit .env):

SECRET_KEY=
DEBUG=True
DATABASE_URL=
RESEND_API_KEY=

Build Approach

Each feature follows this flow before moving to the next:

Build the Django API endpoint → test it
Build the React UI → test integration
Add styling → test again

One feature at a time — no rushing.

Author

Huzaifa Sa'ad (@Houzsaad)