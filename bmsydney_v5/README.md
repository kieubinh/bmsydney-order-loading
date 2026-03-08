# BMSydney Order Capture System

A web application for customer order capture, queue management, and Accrivia XLS export.

## Requirements

- Python 3.x
- Flask (`pip install flask`)
- openpyxl (`pip install openpyxl`)

## Quick Start

```bash
# Install dependencies
pip install flask openpyxl

# Run the application
python app.py
```

Open http://localhost:5000 in your browser.

## Demo Credentials (password: `password123`)

| Role | Email |
|------|-------|
| Customer | customer@test.com |
| Cabramatta CS | cabra_cs@test.com |
| Lidcombe CS | lid_cs@test.com |
| OPS Delivery | ops@test.com |
| Admin | admin@test.com |

## Key Features

### Customer
- Login via email or phone + password
- Create orders manually (search item catalogue)
- Upload scan/document for order entry
- Choose Pickup (Cabramatta or Lidcombe) or Delivery
- View order history and queue number

### Staff
- Role-based queue dashboard (each role sees only their orders)
- Edit order details (address, dates, line items)
- Full audit trail of all changes
- Generate/regenerate Accrivia-compatible XLS
- Download XLS files for Accrivia import
- Update order status (Submitted → InReview → Confirmed → Exported → Completed)

### XLS Output Format (Accrivia Compatible)
- Row 1: Debtor Code
- Row 2: Date (today)
- Row 3: Date Required
- Row 4: Customer Order No
- Row 5: Job Name
- Rows 6–8: Job Address Lines
- Row 11: Headers (Stock Code | Description | Quan)
- Row 12+: Order lines (no price/rate columns ever written)

### Queue Numbering
- Cabramatta pickup: `CAB-YYYYMMDD-###`
- Lidcombe pickup: `LID-YYYYMMDD-###`
- Delivery: `DEL-YYYYMMDD-###`

## File Structure
```
bmsydney/
├── app.py              # Main Flask application
├── bmsydney.db         # SQLite database (auto-created)
├── templates/          # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── customer_dashboard.html
│   ├── new_order.html
│   ├── order_detail.html
│   ├── staff_queue.html
│   ├── staff_order_detail.html
│   └── admin_settings.html
├── generated_xls/      # Generated XLS files stored here
└── uploads/            # Scan/image uploads stored here
```

## Email Configuration

In production, configure SMTP in `app.py` → `send_email_notification()` function,
and set routing addresses via the Admin Settings page or environment variables:
- `CABRA_CS_EMAIL`
- `LIDCOMBE_CS_EMAIL`  
- `OPS_DELIVERY_EMAIL`
