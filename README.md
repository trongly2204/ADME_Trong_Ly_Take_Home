# ADME Lab Portal — Interview Take-Home Test

A Django web application for submitting and tracking in vitro ADME assay requests.

## Background

This is a real-world-style application used as a take-home coding test. The app is functional but deliberately incomplete. Your task is to implement the items listed in `TODO.md`.

---

## Quick Start

### Prerequisites
- Python 3.10+
- Git

### Setup

```bash
# 1. Clone your copy of this repo and create a branch
git checkout -b feature/your-name

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations (creates db.sqlite3 automatically)
python manage.py migrate

# 5. Load the assay catalogue
python manage.py loaddata fixtures/assay_types.json

# 6. Create a superuser
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

Then visit http://localhost:8000

---

## Application Overview

| URL | View | Description |
|-----|------|-------------|
| `/` | Assay Select | Pick an ADME assay from the catalogue |
| `/assay/<id>/upload/` | Upload Compounds | Upload an Excel file of drug samples |
| `/submit/confirm/` | Confirm Submission | Preview and confirm before saving |
| `/requests/mine/` | My Requests | Your submission history |
| `/dashboard/` | Lab Dashboard | All requests; status update controls |
| `/admin/` | Django Admin | Superuser management |

## Data Model

```
AssayType  ──< TestRequest >── Compound
               (requested_by → User)
```

- `AssayType`: catalogue of ADME assays (loaded from fixture)
- `TestRequest`: one submission by one user for one assay
- `Compound`: individual drug samples attached to a request

## Excel Upload Format

Your `.xlsx` file must contain these columns (case-insensitive, any order):

| Column | Type | Example |
|--------|------|---------|
| Drug Name | Text | Acetaminophen |
| Batch Number | Text | BN-2024-001 |
| Container Barcode | Integer | 1000234567 |

---

## Running Tests

```bash
python manage.py test lab --verbosity=2
```

Note - you may need create staticfiles first to run the unit tests:

```bash
python manage.py collectstatic --noinput 2>&1
```

All existing tests must continue to pass after your changes.

---

## Submitting Your Work

1. Commit your changes to your feature branch
2. Push to GitHub
3. Open a Pull Request against `main`
4. The CI pipeline will run automatically — make sure it goes green

See `INSTRUCTIONS.md` for full submission details.
