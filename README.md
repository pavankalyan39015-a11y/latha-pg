# 🏢 Paying Guest (PG) Accommodation Management API

A production-ready, RESTful backend API designed for Paying Guest (PG) owners, managers, and co-living spaces. Built with **FastAPI**, **SQLAlchemy 2.0**, and **Pydantic v2**, supporting both **SQLite** (default zero-config) and **PostgreSQL**.

---

## 🚀 Quick Start

### 1. Navigate to Project Directory
```powershell
cd C:\Users\MSMETC\.gemini\antigravity\scratch\pg_management_api
```

### 2. Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### 3. (Optional) Re-seed Sample Data
Pre-populates 5 rooms, 11 beds, 5 tenants with KYC records, invoices, payments, complaints, and a 7-day mess menu:
```powershell
python seed_data.py
```

### 4. Run the API Server
```powershell
python run.py
```

The server will be live at:
- **API Base URL**: `http://127.0.0.1:8000`
- **Interactive Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc UI**: `http://127.0.0.1:8000/redoc`

---

## 🗄️ Database: Switching to PostgreSQL

By default, the application runs on SQLite (`pg_management.db`). To switch to PostgreSQL:

1. Install psycopg2 / asyncpg:
   ```powershell
   pip install psycopg2-binary
   ```
2. In `.env`, update the `DATABASE_URL`:
   ```ini
   DATABASE_URL=postgresql://username:password@localhost:5432/pg_database
   ```
3. Restart the server or run `python seed_data.py`. All tables will be auto-created in PostgreSQL!

---

## 📡 API Reference Overview

### 📊 Executive Dashboard (`/api/v1/dashboard`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/dashboard/summary` | Real-time overview of occupancy rate, active tenants, pending KYC, dues, and complaints. |

### 🛏️ Rooms & Beds (`/api/v1/rooms`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/rooms` | List all rooms (filter by `floor`, `room_type`, `has_ac`). |
| `POST` | `/api/v1/rooms` | Create a room (auto-generates beds like `101-A`, `101-B`). |
| `GET` | `/api/v1/rooms/{room_id}` | Get room details and bed occupancy. |
| `PUT` | `/api/v1/rooms/{room_id}` | Update room rent, amenities, AC status. |
| `DELETE` | `/api/v1/rooms/{room_id}` | Delete room (disallowed if beds are occupied). |
| `POST` | `/api/v1/rooms/{room_id}/beds` | Add a bed slot to a room. |
| `GET` | `/api/v1/rooms/beds/available` | List all vacant beds ready for assignment. |
| `PATCH` | `/api/v1/rooms/beds/{bed_id}/status` | Update bed status (`AVAILABLE`, `OCCUPIED`, `MAINTENANCE`). |
| `DELETE` | `/api/v1/rooms/beds/{bed_id}` | Delete an unoccupied bed slot from a room. |

### 👤 Tenants & KYC (`/api/v1/tenants`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/tenants` | List tenants (filter by `is_active`, `kyc_status`, search by name/phone). |
| `POST` | `/api/v1/tenants/onboard` | Onboard tenant, assign bed, lock bed as `OCCUPIED`. |
| `GET` | `/api/v1/tenants/{tenant_id}` | Full tenant profile with KYC documents. |
| `PUT` | `/api/v1/tenants/{tenant_id}` | Update tenant info, verify KYC, or shift beds. |
| `DELETE` | `/api/v1/tenants/{tenant_id}` | Delete tenant record and release allocated bed. |
| `POST` | `/api/v1/tenants/{tenant_id}/documents` | Upload/record KYC document (Aadhaar, Passport, ID card). |
| `POST` | `/api/v1/tenants/{tenant_id}/checkout` | Check out tenant, record date, release bed to `AVAILABLE`. |

### 💳 Billing, Rent & Payments (`/api/v1/billing`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/billing/invoices` | List invoices (filter by `tenant_id`, `billing_month`, `status`). |
| `POST` | `/api/v1/billing/invoices` | Generate invoice (rent + utilities + late fee - discount). |
| `GET` | `/api/v1/billing/invoices/{invoice_id}` | Get invoice with payment receipts. |
| `PATCH` | `/api/v1/billing/invoices/{invoice_id}` | Update invoice details, charges, discount, or status. |
| `POST` | `/api/v1/billing/payments` | Record payment (UPI, Cash, Bank Transfer) & auto-settle unpaid invoices. |
| `GET` | `/api/v1/billing/payments` | List payment collection receipts. |
| `GET` | `/api/v1/billing/payments/{payment_id}/receipt` | Get official printable receipt details. |
| `GET` | `/api/v1/billing/tenants/{tenant_id}/dues` | Calculate net outstanding dues and unpaid invoices. |

### 🛠️ Maintenance & Complaints (`/api/v1/complaints`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/complaints` | List tickets (filter by `status`, `priority`, `category`). |
| `POST` | `/api/v1/complaints` | Raise a complaint ticket (`TKT-XXXX`). |
| `GET` | `/api/v1/complaints/{ticket_id}` | Get ticket details and resolution status. |
| `PATCH` | `/api/v1/complaints/{ticket_id}` | Update status (`OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`). |

### 🍽️ Mess & Meal Management (`/api/v1/meals`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/meals/menu` | View weekly meal schedule (filter by `day`, `meal_type`). |
| `POST` | `/api/v1/meals/menu` | Add/update meal menu item. |
| `POST` | `/api/v1/meals/attendance` | Record meal attendance, opt-out, or packed meal request. |
| `GET` | `/api/v1/meals/headcount` | Kitchen headcount calculation for preparing food. |

---

## 🧪 Automated Testing
Run the automated test suite anytime:
```powershell
python test_api.py
```

---

## 📱 Mobile App & Android APK Support

The system supports native Android mobile usage and Progressive Web App (PWA) installation:

- **Instant Mobile App (PWA)**: Open the server URL (or Cloudflare URL from `share_mobile.bat`) on your Android phone and tap **Install App** to add it to your home screen with a native icon and full-screen experience.
- **Android APK Project**: The complete Android Studio project is available in [`android/`](file:///android/).
- **Automated Cloud Build**: Push to GitHub to trigger [`.github/workflows/build-apk.yml`](file:///.github/workflows/build-apk.yml) and download the generated `app-debug.apk`.
- **PWABuilder 1-Click APK**: Follow the step-by-step instructions in [build_apk_guide.md](file:///build_apk_guide.md) to generate an APK in 60 seconds.

