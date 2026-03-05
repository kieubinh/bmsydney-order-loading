# Developer Execution Plan (Tasks, Repo Structure, Tests)

## 0) Build Targets
Deliver a working MVP with:
- Customer login (email/phone + password)
- Manual order entry
- Pickup/delivery selection + required fields
- Submit → queue number → XLS generation → email routing
- Staff portal: queue list + order detail + edit + regenerate XLS + download
- Audit log for staff edits/status changes
- Minimal XLS (fixed mapping, no styles, no price cells)

Phase 2 (optional after MVP):
- Scan upload + OCR draft table + user review

---

## 1) Suggested Tech Choices (Codex may choose, but must be consistent)
Pick one stack and implement fully:

### Option A (Node/TypeScript)
- Next.js (App Router) + API routes or separate Express/NestJS
- PostgreSQL + Prisma
- XLS export: `exceljs`
- Auth: NextAuth (credentials) or custom JWT
- Email: SMTP or provider (SendGrid/Mailgun)

### Option B (.NET)
- ASP.NET Core Web API + Razor/React frontend
- SQL Server or PostgreSQL
- XLS export: EPPlus / OpenXML
- Auth: ASP.NET Identity + JWT
- Email: SMTP

Regardless of stack:
- Provide Docker Compose for DB + app (dev)
- Use environment variables for secrets and email routing addresses

---

## 2) Repo Structure (example, adjust to chosen stack)

### Node/Next.js example
```
/apps/web
  /app
  /app/(auth)
  /app/customer
  /app/staff
  /app/admin
  /api
  /components
  /lib
/prisma
  schema.prisma
/tests
  xls-export.test.ts
  validation.test.ts
  api-auth.test.ts
/docs
  SPEC.md
  EXECUTION_PLAN.md
/docker-compose.yml
/.env.example
/README.md
```

### .NET example
```
/src
  /Api
  /Web
  /Domain
  /Infrastructure
/tests
  /Api.Tests
  /Xls.Tests
/docs
  SPEC.md
  EXECUTION_PLAN.md
/docker-compose.yml
/.env.example
/README.md
```

---

## 3) Work Breakdown Structure (Do in this order)

### 3.1 Project scaffolding
- [ ] Initialize repo + chosen stack
- [ ] Add Docker Compose (DB + app)
- [ ] Add `.env.example` (DB_URL, SMTP settings, routing email addresses)
- [ ] Add `/docs/SPEC.md` and `/docs/EXECUTION_PLAN.md`

### 3.2 Database schema + migrations
Create tables/entities:
- [ ] Users (email/phone, password_hash, role)
- [ ] Orders
- [ ] OrderLines
- [ ] ItemMaster
- [ ] DebtorMaster (optional in MVP; can stub)
- [ ] OrderAttachments
- [ ] AuditLog
- [ ] QueueCounter (for per-queue numbering)

Migration rules:
- [ ] Ensure unique index on email and phone (nullable-safe)
- [ ] Foreign keys: orders → users, orderlines → orders, audit → orders/users

### 3.3 Authentication + RBAC
- [ ] Credential login supports email OR phone
- [ ] Password hashing (bcrypt/argon2)
- [ ] JWT or session cookies
- [ ] Role-based guards:
  - Customer endpoints require CUSTOMER
  - Staff endpoints require matching role
  - Admin endpoints require ADMIN
- [ ] Rate limiting login attempts

### 3.4 Item master endpoints (MVP)
- [ ] Seed a small ItemMaster dataset for dev
- [ ] API: GET `/api/items?search=`
  - returns item_code, description, active_flag
- [ ] Server-side validation must check ItemMaster active_flag

(If debtor code mapping is not finalized, use Model A: system assigns debtor code.)

### 3.5 Customer UI (Manual Order Entry)
Pages:
- [ ] Login page
- [ ] Customer dashboard (order list)
- [ ] New Order page:
  - choose Pickup/Delivery
  - pickup: choose Cabramatta/Lidcombe
  - delivery: required date + address + contact number
  - fulfilment note field
  - item search/select table:
    - add/remove line
    - qty input
    - prevent blank qty
- [ ] Submit flow:
  - calls submit endpoint
  - shows confirmation: Order ID + Queue Number

### 3.6 Order API (Customer)
- [ ] POST `/api/orders` create draft
- [ ] POST `/api/orders/{id}/submit`
  - Validate header + lines
  - Assign queue number
  - Generate XLS v1
  - Send email (route by pickup store or delivery)
  - Set status Submitted
  - Write audit log entries

### 3.7 Queue number generator
Implement deterministic queue policy:
- [ ] Separate counters:
  - PICKUP_CABRA
  - PICKUP_LIDCOMBE
  - DELIVERY_OPS
- [ ] Queue number format recommended:
  - `CAB-YYYYMMDD-###`
  - `LID-YYYYMMDD-###`
  - `DEL-YYYYMMDD-###`
- [ ] Reset daily (counter keyed by queue + date)

### 3.8 XLS generator module (Core)
Implement `generateAccriviaXls(order, version)`:

Must:
- [ ] Create `.xlsx` with one sheet `Sheet1`
- [ ] A1 = debtor code
- [ ] A2 = date (default today)
- [ ] A3 = required date (default today)
- [ ] Rows 4–8 mapping:
  - Use config mapping; default to proposed mapping in SPEC
- [ ] Row 12+:
  - Column A = item_code
  - Column B = quantity
- [ ] No formulas, no styles, no extra sheets
- [ ] Never write price fields/cells

File storage:
- [ ] Save generated XLS as attachment:
  - type = GeneratedXLS
  - version_no increments
  - created_by = system or staff
- [ ] Allow staff to download latest version

### 3.9 Email module + routing
- [ ] Implement email sender using SMTP/provider
- [ ] Configurable routing addresses:
  - CABRA_CS_EMAIL
  - LIDCOMBE_CS_EMAIL
  - OPS_DELIVERY_EMAIL
- [ ] Email content includes:
  - Order summary + queue number
  - Staff portal link
  - Items list
  - Attach XLS v1 OR include secure download link
- [ ] Persist email send result (success/failure) to logs + order notes

### 3.10 Staff UI + workflow
Pages:
- [ ] Staff queue dashboard:
  - filter by role automatically
  - sorted by queue number ascending
- [ ] Order detail page:
  - view customer details + items + notes
  - edit allowed fields (depending on order type):
    - required date
    - address/contact (delivery)
    - fulfilment note
    - item lines (qty changes, substitutions)
    - internal notes
  - status actions:
    - InReview
    - Confirmed
    - Exported
    - Completed
- [ ] Generate XLS (Confirmed Version):
  - button creates new XLS version and attaches to order
  - download button for latest XLS

Audit:
- [ ] Every staff update writes AuditLog with JSON diff

### 3.11 Admin settings (lightweight MVP)
- [ ] Settings page or config endpoints for:
  - routing emails
  - header field mapping rows 4–8
  - queue reset policy (daily/continuous)
- [ ] Store settings in DB table `AppSettings` or environment variables initially (DB preferred)

---

## 4) Testing Plan (Must Implement)

### 4.1 Unit tests — validation
- [ ] Reject invalid item codes
- [ ] Reject inactive item codes
- [ ] Reject qty <= 0 or non-numeric
- [ ] Delivery requires address + contact
- [ ] Pickup requires store
- [ ] Required date defaults to today if missing (as per SPEC)

### 4.2 Unit tests — queue numbering
- [ ] Queue increments sequentially per queue per day
- [ ] Cabramatta pickup and Lidcombe pickup counters are independent
- [ ] Delivery counter independent
- [ ] Reset daily behavior works (new date starts at 001)

### 4.3 Unit tests — XLS export “golden file”
Create deterministic export tests:
- [ ] Generate XLS for a known order
- [ ] Read back the XLS and assert:
  - Sheet1 exists only
  - A1/A2/A3 values correct
  - Rows 12+ have correct item_code/qty
  - No unexpected populated cells outside allowed mapping
- [ ] Test that “price” is never written:
  - search the workbook for numeric cells outside qty column / allowed cells
  - assert blank

### 4.4 Integration tests — submit flow
- [ ] Create customer + login
- [ ] Create order + submit
- [ ] Verify:
  - status becomes Submitted
  - queue number assigned
  - attachment created (GeneratedXLS v1)
  - email send attempted (mock in test env)

### 4.5 RBAC tests
- [ ] Customer cannot access staff endpoints
- [ ] CS-CABRA cannot view Lidcombe queue (unless ADMIN)
- [ ] OPS-DELIVERY cannot edit pickup order (unless ADMIN)

---

## 5) Dev Seed Data (Required)
- [ ] Seed ItemMaster with 100 sample items:
  - `ITEM0001`..`ITEM0100` + descriptions
- [ ] Seed staff users:
  - cabra_cs@test.com (CS-CABRA)
  - lid_cs@test.com (CS-LIDCOMBE)
  - ops@test.com (OPS-DELIVERY)
  - admin@test.com (ADMIN)
- [ ] Seed one customer:
  - customer@test.com / phone + password

---

## 6) Phase 2 Add-on: Scan Upload + OCR Draft (Stub first)
MVP stub (must be implemented even if OCR not):
- [ ] Customer can upload scan image
- [ ] System stores attachment as ScanImage
- [ ] Provide a manual “enter extracted lines” table (user typed)
- [ ] Later replace with OCR extraction service (optional)

If OCR is implemented:
- [ ] Use an OCR library/service
- [ ] Return extracted candidates with confidence
- [ ] Require user confirmation before submit

---

## 7) Deployment & Ops
- [ ] Docker compose for dev
- [ ] Basic production config notes in README:
  - DB migration command
  - storage config
  - SMTP config
- [ ] Logging: stdout + error logs
- [ ] Health endpoint `/health`

---

## 8) Definition of Done
- [ ] MVP flows work end-to-end in local dev environment
- [ ] Tests pass
- [ ] README includes setup steps + seed credentials
- [ ] XLS output confirmed to match fixed mapping and imports into Accrivia in a manual test

---

## 9) Notes / Constraints
- Do not allow customer to upload XLS in MVP.
- Generate XLS server-side only.
- Keep XLS minimal to reduce Accrivia slowdown.
- All staff edits must be in portal; XLS is regenerated from DB state.
- If “Upload adjusted XLS” is required later, implement strict validator and keep it staff-only.
