# BMSYDNEY Order Capture → Queue → Accrivia XLS Export System (Specification)

## 0) Purpose
Build a web system where **customers log in**, create orders either **manually** or via **image/scan assisted entry**, choose **pickup or delivery**, then **submit**. The system generates an **Accrivia-compatible XLS** (fixed structure) and routes the order to the correct internal team via email. Staff then **confirm with customer**, adjust order details (delivery fees, notes, changes), regenerate the XLS, and proceed with normal Accrivia import.

Primary goals:
- Reduce customer service time spent retyping orders
- Prevent incorrect debtor/item codes
- Prevent **price manipulation** via XLS
- Provide queue + audit trail + consistent XLS output for Accrivia import

---

## 1) Users and Roles

### 1.1 Customer
- Logs in with **email or phone + password**
- Can create orders (manual or scan)
- Can submit orders and view order status/history
- Cannot set any price or cost fields

### 1.2 Staff Roles
- **Cabramatta Customer Service (CS-CABRA)**
  - Views/handles pickup orders for Cabramatta
- **Lidcombe Customer Service (CS-LIDCOMBE)**
  - Views/handles pickup orders for Lidcombe
- **Order Processing Team (OPS-DELIVERY)**
  - Views/handles delivery orders
- **Admin/Supervisor (ADMIN)**
  - Can view all orders, configure routing emails, manage item/debtor master data sync, manage users/roles

---

## 2) Customer Flow (Must Match)

### Step A — Login
- Customers authenticate using:
  - identifier: email OR phone
  - password
- Provide password reset.

### Step B — Create Order (Two options)

#### Option 1: Manual Order Entry (Default)
- Customer selects **Pickup** or **Delivery**
- Customer enters header information (see Section 5: XLS mapping)
- Customer selects items from an **Item Master List** that shows:
  - Item Code
  - Description
  - (Optional) Unit of measure / pack size if available
- Customer enters Quantity per item
- Customer can add a general note (fulfilment note)

#### Option 2: Upload Image / Scan (Assisted Entry)
- Customer uploads an image or scan containing a list of:
  - item code + quantity (at minimum)
- System performs OCR/extraction to create a **draft item list**
- Customer must review/edit extracted lines (mandatory)
- Customer proceeds to submit

**Important:** scan/OCR must never auto-submit. It must be “draft → review → submit”.

### Step C — Pickup/Delivery Details

#### Pickup
- Customer selects store:
  - Cabramatta OR Lidcombe
- Customer can add pickup note (maps to fulfilment note)
- Required date optional (can default to today)

#### Delivery
- Customer must input:
  - Required date
  - Delivery address
  - Contact number
- Customer can add delivery instructions note

### Step D — Submit
- On submit:
  - System validates debtor code (if used) and item codes + quantities
  - System assigns **Queue Number** (see Section 6)
  - System generates a fixed-structure **Accrivia XLS**
  - System sends email to the correct team based on order type/store
  - Customer sees confirmation screen with:
    - Order ID
    - Queue Number
    - Summary

---

## 3) Staff Flow (Must Match)

### Step E — Work Queue
- Staff see a queue filtered by their role:
  - CS-CABRA: Cabramatta pickup
  - CS-LIDCOMBE: Lidcombe pickup
  - OPS-DELIVERY: delivery
- Queue sorted by **Queue Number ascending** (first come, first served)

### Step F — Contact and Confirm
- Staff contact customer:
  - Pickup: if customer already at store, confirm directly
  - Delivery: OPS calls customer to confirm details
- Staff updates order in staff portal:
  - Adjust required date/address/contact if needed
  - Add delivery fee or additional information if needed
  - Add internal notes
  - Substitute items / change quantities if required (with audit trail)

### Step G — Regenerate XLS and Process Normally
- Staff clicks “Generate XLS (Confirmed Version)”
- Staff downloads confirmed XLS for import into Accrivia
- Staff marks order status as:
  - Confirmed → Exported → Completed (as they progress)

---

## 4) Data Requirements (Core Entities)

### 4.1 User
- id
- role (Customer, CS-CABRA, CS-LIDCOMBE, OPS-DELIVERY, ADMIN)
- email (nullable if phone used)
- phone (nullable if email used)
- password_hash
- name
- created_at, updated_at
- last_login_at

### 4.2 CustomerProfile (optional but helpful)
- user_id
- default_contact_number
- default_delivery_address fields
- preferred_store (Cabramatta/Lidcombe)

### 4.3 Order
- id (UUID or numeric)
- order_number (human readable)
- queue_number (per queue policy)
- customer_user_id
- order_type: Pickup | Delivery
- pickup_store: Cabramatta | Lidcombe | null
- required_date (date)
- delivery_address (string or structured fields)
- contact_number (string)
- fulfilment_note (string)  // includes your “pickup/delivery notes”
- source: Manual | Scan
- status: Draft | Submitted | InReview | Confirmed | Exported | Completed | Cancelled
- submitted_at
- confirmed_at
- created_at, updated_at

### 4.4 OrderLine
- id
- order_id
- line_no
- item_code
- item_description (snapshotted at time of order)
- quantity (decimal)
- customer_line_note (optional)
- created_at, updated_at

### 4.5 ItemMaster
- item_code (PK)
- description
- active_flag
- last_sync_at

### 4.6 DebtorMaster (if debtor code is required)
- debtor_code (PK)
- debtor_name
- active_flag
- last_sync_at

### 4.7 OrderAttachment (for scan images and/or uploaded confirmed XLS if needed)
- id
- order_id
- type: ScanImage | GeneratedXLS | UploadedXLS
- file_path / blob reference
- version_no (1,2,3…)
- created_by_user_id
- created_at

### 4.8 AuditLog (must-have)
- id
- order_id
- actor_user_id
- action_type (Create/Update/StatusChange/Export/etc.)
- changes (JSON diff)
- created_at

---

## 5) Accrivia XLS Output Specification (Fixed Structure)

### 5.1 General Rules
- Output is an Excel file (.xlsx) with a single sheet named `Sheet1`.
- No formulas, no macros, no heavy styling.
- Only write required cells; leave others blank.
- Must never write any “price” fields/cells/columns.
- Rows are 1-indexed in this spec.

### 5.2 Required Row Mapping (Minimum)
- **Row 1 (A1): Debtor Code**
- **Row 2 (A2): Date** (default to today if missing)
- **Row 3 (A3): Date Required** (default to today if missing)
- **Row 12 onward:** line items
  - Column A: Item Code
  - Column B: Quantity
  - Unlimited lines until end

### 5.3 Header Fields Rows 4–8 (Your “rows 1–8” equivalent)
You said: “Customer fills rows 1 to 8” and “Row 8 (Job Address Line 3) used for fulfilment note”.

Define these header rows explicitly for the system (so Codex can build correctly):

**Proposed mapping (editable in config later):**
- Row 4 (A4): Customer Reference / PO Number (optional)
- Row 5 (A5): Job Address Line 1 (Delivery address line 1 OR pickup note)
- Row 6 (A6): Job Address Line 2
- Row 7 (A7): Job Address Line 3
- Row 8 (A8): Job Address Line 4 / Fulfilment Note (REQUIRED for fulfilment note usage)

If you already have the exact Accrivia template fields for rows 4–8, replace the above mapping with your exact field names. The system should treat these as **fixed positions**.

### 5.4 Versioning
- Every time staff regenerates XLS after confirmation, create a new version:
  - GeneratedXLS v1 (submitted)
  - GeneratedXLS v2 (confirmed)
  - etc.
- Staff should export the latest “Confirmed” XLS.

---

## 6) Validation and Business Rules

### 6.1 Authentication
- Email or phone must be unique per user.
- Rate limit login attempts.

### 6.2 Order Header Validation
- Required date:
  - If missing: default to today
  - For delivery: enforce user provides it OR default with warning (choose one; recommended: require it)
- Delivery address and contact number:
  - Required when order_type = Delivery
- Pickup store:
  - Required when order_type = Pickup

### 6.3 Item Line Validation
- Item Code must exist in ItemMaster and be active
- Quantity must be numeric and > 0
- Duplicate item codes:
  - Either merge quantities automatically OR allow duplicates but warn (recommended: auto-merge)

### 6.4 Debtor Code Validation
Two workable models; pick one:

**Model A (recommended for safety):**
- Customer does not enter debtor code.
- System assigns debtor code based on customer account mapping.
- For special cases, allow “Credit Cabra” and “Credit Lidcombe”.

**Model B (if you must allow input):**
- Customer can choose debtor code from a list available to their account.
- Never allow free text debtor code input.

### 6.5 Price Control (Critical)
- Customer UI must not contain any price fields.
- XLS generator must never write any price cells/columns anywhere.
- If staff upload XLS (optional feature), system must reject files containing:
  - any unexpected sheets
  - any populated cells outside the allowed mapping
  - any values in known price columns/ranges (if applicable)

---

## 7) Queue Number Rules
- Queue number is assigned at **submission time**.
- Queue numbering policy:
  - For pickup: separate queues per store (Cabramatta and Lidcombe)
  - For delivery: separate queue for OPS
- Queue number increments sequentially per queue and resets daily OR never resets (choose one):
  - Recommended: reset daily to keep numbers small + meaningful (e.g., CAB-20260304-012)
- Queue number must be unique within its queue and date.

---

## 8) Email Routing Requirements

### 8.1 Routing logic
- If Pickup + Cabramatta → email Cabramatta CS inbox
- If Pickup + Lidcombe → email Lidcombe CS inbox
- If Delivery → email Order Processing inbox

### 8.2 Email content
Subject format (example):
- `[Order Queue #{queue_number}] {Pickup/Delivery} - {Customer Name} - {Required Date}`

Body must include:
- Customer name + contact number
- Pickup store OR delivery address
- Required date
- Fulfilment note
- Item list (code, description, qty)
- Link to open order in staff portal
- Order ID and Queue number

Attachment:
- Attach GeneratedXLS v1 OR provide secure download link (either acceptable)
- Recommended: attach XLS + link for redundancy

---

## 9) Screens / Pages (Minimum UI)

### 9.1 Customer screens
- Login
- Forgot password / reset
- Dashboard / Order history
- New Order: Manual
- New Order: Scan/Upload (with OCR review table)
- Order detail view (read-only after submit unless you allow editing before staff picks it up)

### 9.2 Staff screens
- Queue dashboard (filtered by role)
- Order detail (editable fields + audit history)
- Generate/Download XLS (shows versions)
- Status updates
- Admin configuration:
  - routing emails
  - queue policy (reset daily vs continuous)
  - header field mapping for rows 4–8
  - item/debtor master sync options

---

## 10) API Requirements (High-Level)
Codex can implement REST or GraphQL. Minimum endpoints:

Auth:
- POST /api/auth/login
- POST /api/auth/reset-request
- POST /api/auth/reset

Customer:
- GET /api/items?search=
- POST /api/orders (create draft)
- POST /api/orders/{id}/submit
- POST /api/orders/{id}/scan-upload (upload image)
- GET /api/orders (customer’s orders)
- GET /api/orders/{id}

Staff:
- GET /api/staff/queue?type=pickup&store=cabra
- GET /api/staff/orders/{id}
- PATCH /api/staff/orders/{id} (edits)
- POST /api/staff/orders/{id}/status
- POST /api/staff/orders/{id}/export-xls (generate new version)
- GET /api/staff/orders/{id}/attachments

Admin:
- GET/PUT /api/admin/settings (routing emails, mappings, queue policy)
- POST /api/admin/sync/items
- POST /api/admin/sync/debtors

---

## 11) Non-Functional Requirements
- Audit logging for all staff edits and status changes
- File storage for scan uploads and generated XLS (local dev + production-compatible)
- Input validation + server-side sanitization
- Rate limiting on login and upload
- Performance:
  - XLS generator must produce minimal files (no styles) to reduce Accrivia slowdowns
- Observability:
  - basic logs (submission, email send, export actions)
  - email send failures must be visible in staff/admin UI

---

## 12) Acceptance Criteria (Testable)

### Customer
1) Customer can log in using email/password or phone/password.
2) Customer can create an order manually by selecting items from item master list.
3) Customer can create an order via scan upload; system extracts lines; customer must confirm/edit before submission.
4) Customer must choose pickup store for pickup, and must enter address/contact for delivery.
5) On submit:
   - queue number is assigned
   - order is emailed to the correct team
   - XLS is generated with fixed mapping and no price cells

### Staff
6) Staff queue shows correct orders by role and sorted by queue number.
7) Staff can edit confirmed details (notes, delivery fee info, substitutions) with audit log.
8) Staff can regenerate XLS; each regeneration creates a new version.
9) Staff can download the latest confirmed XLS.

### XLS
10) Generated XLS always matches:
   - A1 debtor code
   - A2 date (default today)
   - A3 required date (default today)
   - Row 12+: item code in col A, qty in col B
   - No price cells written anywhere

### Email
11) Email routing is correct for Cabramatta pickup, Lidcombe pickup, and delivery orders.
12) Email contains summary + staff portal link + XLS attachment or download link.

---

## 13) Build Phases (Recommended)

### Phase 1 (MVP)
- Login
- Manual order entry
- Pickup/delivery
- Submit → queue number → XLS generation → email routing
- Staff portal queue + confirm edits + regenerate XLS + download

### Phase 2
- Scan/OCR assisted entry with review UI
- Order history improvements
- Notifications (optional SMS)

### Phase 3
- Debtor mapping per customer account
- Favorites/reorder
- Accrivia integration automation if possible

---

## 14) Configuration Items (Admin)
- Email routing addresses for:
  - Cabramatta CS
  - Lidcombe CS
  - Order Processing
- Queue numbering policy: reset daily or continuous
- Header rows 4–8 mapping (labels and which field maps to which row)
- Item/debtor master data source + sync schedule/manual sync

---

### Notes to Codex (Implementation Guidance)
- Keep XLS generator minimal: no formatting, no formulas.
- Treat scan upload as “draft extraction” only; must require user confirmation.
- Implement strict role-based access for staff/admin endpoints.
- Store all generated XLS versions for traceability.
