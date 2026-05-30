# TODO — Candidate Tasks

Complete as many of these as you can within the time allowed (we suggest 3–4 hours). You do not need to finish everything — we value working code and clear reasoning over quantity.

---

## Task 1 — Filter the Lab Dashboard by status  *(required)*

The lab dashboard at `/dashboard/` currently shows all requests regardless of status.

**Your task:**
- Add a filter control (dropdown or button group) above the table that lets the scientist filter by status: All / Pending / In Progress / Complete / On Hold.
- Filtering should work without a page reload (JavaScript) **or** via a query parameter (either approach is acceptable).
- The currently-active filter should be visually indicated.

**Write at least one test** that verifies the filter returns only the expected requests.

---

## Task 2 — Validate that barcodes are unique within a submission  *(required)*

The spreadsheet parser currently accepts duplicate `Container Barcode` values within the same upload without complaint.

**Your task:**
- Add validation in `lab/utils.py` to raise a `SpreadsheetParseError` if any barcode appears more than once in the same file.
- Add tests covering both the duplicate case (should raise) and the valid case (should not raise).

---

## Task 3 — Add a compound count badge to the assay cards  *(stretch)*

The assay selection page (`/`) shows catalogue cards for each assay. It would be useful for scientists to see how many pending requests exist for each assay.

**Your task:**
- Annotate the assay queryset in the `assay_select` view with a count of pending `TestRequest` objects.
- Display this count as a badge on each assay card (e.g. "3 pending").
- Show nothing (or "0") if there are no pending requests.

---

## Task 4 — Add a `priority` field to TestRequest  *(stretch)*

The lab wants to prioritise urgent requests.

**Your task:**
- Add a `priority` field to `TestRequest` with choices: Normal, High, Urgent.
- Default to Normal.
- Write and apply the migration.
- Display the priority on both the "My Requests" and "Lab Dashboard" views.
- Allow the scientist to update priority alongside status on the dashboard.

---

## Notes

- Keep your code clean and readable — we will review it as if it were a real PR.
- Write docstrings for any new functions.
- All existing tests must still pass.
- If you run out of time, leave a comment in the code explaining what you would have done next.
