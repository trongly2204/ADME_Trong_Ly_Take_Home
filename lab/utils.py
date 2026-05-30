"""Utility functions for parsing compound spreadsheets."""

import openpyxl


REQUIRED_COLUMNS = {'drug name', 'batch number', 'container barcode'}


class SpreadsheetParseError(Exception):
    pass


def parse_compound_spreadsheet(file_obj):
    """
    Parse an uploaded .xlsx file into a list of compound dicts.

    Expected columns (case-insensitive):
        Drug Name | Batch Number | Container Barcode

    Returns:
        list of dicts: [{'drug_name': str, 'batch_number': str, 'container_barcode': int}, ...]

    Raises:
        SpreadsheetParseError: if the file cannot be parsed or columns are missing.
    """
    try:
        wb = openpyxl.load_workbook(file_obj, read_only=True, data_only=True)
    except Exception as exc:
        raise SpreadsheetParseError(f"Could not open spreadsheet: {exc}") from exc

    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))

    if not rows:
        raise SpreadsheetParseError("The spreadsheet appears to be empty.")

    # Normalise headers
    headers = [str(h).strip().lower() if h is not None else '' for h in rows[0]]

    missing = REQUIRED_COLUMNS - set(headers)
    if missing:
        raise SpreadsheetParseError(
            f"Missing required columns: {', '.join(sorted(missing))}. "
            f"Found: {', '.join(h for h in headers if h)}"
        )

    name_idx = headers.index('drug name')
    batch_idx = headers.index('batch number')
    barcode_idx = headers.index('container barcode')

    compounds = []
    errors = []

    for row_num, row in enumerate(rows[1:], start=2):
        drug_name = row[name_idx]
        batch_number = row[batch_idx]
        barcode_raw = row[barcode_idx]

        # Skip entirely blank rows
        if all(v is None for v in row):
            continue

        row_errors = []
        if not drug_name:
            row_errors.append("missing drug name")
        if not batch_number:
            row_errors.append("missing batch number")

        try:
            barcode = int(barcode_raw)
        except (TypeError, ValueError):
            row_errors.append(f"invalid barcode '{barcode_raw}' (must be an integer)")
            barcode = None

        if row_errors:
            errors.append(f"Row {row_num}: {'; '.join(row_errors)}")
            continue

        compounds.append({
            'drug_name': str(drug_name).strip(),
            'batch_number': str(batch_number).strip(),
            'container_barcode': barcode,
        })

    if errors:
        raise SpreadsheetParseError(
            f"Found {len(errors)} row error(s):\n" + "\n".join(errors)
        )

    if not compounds:
        raise SpreadsheetParseError("No valid compound rows found in the spreadsheet.")

    #Raise error if duplicate barcode in 1 file
    seen = set()
    duplicates = set()
    for compound in compounds:
        barcode = compound['container_barcode']
        if barcode in seen:
            duplicates.add(barcode)
        seen.add(barcode)

    if duplicates:
        raise SpreadsheetParseError(
            f"Duplicate barcode(s) found: {', '.join(str(b) for b in sorted(duplicates))}"
        )

    return compounds
