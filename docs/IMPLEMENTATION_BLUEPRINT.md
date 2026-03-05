# Implementation Blueprint — BMSydney Order Loading

## 1) Scope and MVP Decision
This blueprint converts the requested user flow into an implementable MVP (Phase 1), aligned to the existing repo spec and execution plan.

MVP includes:
- Login via email **or** phone + password.
- Manual order entry from Item Master.
- Pickup/Delivery branching with required fields.
- Submit flow with queue number, XLS generation, and role-based email routing.
- Staff queue + confirmation edits + regenerate XLS.

Deferred to Phase 2:
- Image/scan OCR-assisted order capture (upload + extraction + mandatory review before submit).

---

## 2) End-to-End User Flow (Finalized)

### Customer flow
1. Customer logs in using email/phone and password.
2. Customer starts a new order.
3. Customer selects one of:
   - **Option 1 (MVP):** manual item entry.
   - **Option 2 (Phase 2):** upload image/scan for OCR draft, then must review and edit.
4. Customer chooses fulfilment type:
   - **Pickup:** choose `Cabramatta` or `Lidcombe`.
   - **Delivery:** enter required date, address, and contact number.
5. Customer submits order.
6. System validates data, assigns queue number, generates XLS, emails correct team.
7. Customer sees confirmation with order ID + queue number.

### Staff flow
1. Staff opens role-specific queue:
   - CS-CABRA = Cabramatta pickup.
   - CS-LIDCOMBE = Lidcombe pickup.
   - OPS-DELIVERY = delivery orders.
2. Staff contacts customer and confirms details.
3. Staff edits order details if required (notes, delivery details, line changes).
4. Staff regenerates XLS (new version) and imports to Accrivia.

---

## 3) XLS Mapping Based on Current Template
Using `data/test_template.xlsx` as the baseline template structure:

## Header rows
- `A1/B1`: Debtor Code label/value
- `A2/B2`: Date label/value
- `A3/B3`: Date Required label/value
- `A4/B4`: Customer Order No
- `A5/B5`: Job Name
- `A6/B6`: Job Address Line 1
- `A7/B7`: Job Address Line 2
- `A8/B8`: Job Address Line 3

## Line table
- Row 11 = headers
- Row 12+ = order lines
  - `A`: Stock Code
  - `B`: Description (optional snapshot)
  - `C`: Quantity

## Control rules
- Generate only one sheet: `Sheet1`.
- Never write any price/rate fields (e.g., do not write col `D` rate values).
- Keep file minimal (no formulas/macros/styling changes).

---

## 4) Data Model (MVP)
Minimum entities:
- `User` (role, email, phone, password hash)
- `Order` (type, pickup_store, delivery fields, queue number, status)
- `OrderLine` (item_code, qty, description snapshot)
- `ItemMaster` (active item codes)
- `OrderAttachment` (generated XLS versions)
- `AuditLog` (staff edits/status transitions)
- `QueueCounter` (per queue per day)

---

## 5) Queue Number Strategy
Daily reset counters, independent by queue:
- `CAB-YYYYMMDD-###`
- `LID-YYYYMMDD-###`
- `DEL-YYYYMMDD-###`

Assigned exactly once on submit.

---

## 6) Email Routing Rules
- Pickup + Cabramatta → Cabramatta CS inbox.
- Pickup + Lidcombe → Lidcombe CS inbox.
- Delivery → Order Processing inbox.

Email payload includes:
- order ID, queue number, customer info,
- pickup/delivery details,
- item table,
- staff portal link,
- XLS attachment (preferred) or secure download URL.

---

## 7) Validation Rules
- Login identifier can be email or phone.
- Pickup requires store selection.
- Delivery requires required date + address + contact.
- Item code must exist and be active.
- Quantity must be numeric and > 0.
- Duplicate item codes should be auto-merged before submit.

---

## 8) Suggested Delivery Plan

### Phase 1 (4–6 weeks)
- Auth + RBAC
- Item master search
- Manual order entry
- Submit pipeline (validate → queue → XLS → email)
- Staff queue/detail/edit workflow
- XLS versioning + download
- Tests: validation, queue numbering, XLS golden file

### Phase 2 (2–4 weeks)
- Scan/image upload
- OCR extraction service integration
- Review-and-confirm UI before submit

### Phase 3 (optional)
- Debtor auto-mapping by customer profile
- Better notifications (SMS/WhatsApp)
- ERP integration hardening

---

## 9) Immediate Next Steps
1. Confirm XLS column mapping policy (template indicates quantity in column `C`).
2. Confirm debtor-code assignment model (recommended: system-assigned, not free text).
3. Finalize SMTP routing addresses for three inboxes.
4. Start MVP implementation from Phase 1 checklist in `docs/EXECUTION_PLAN.md`.
