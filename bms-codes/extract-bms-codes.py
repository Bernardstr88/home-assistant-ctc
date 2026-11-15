from pathlib import Path
import csv

import camelot

PDF_PATH = Path("Manual-BMS Manual-16260016-2.pdf")
OUTPUT_DIR = Path("extracted_tables")
PAGES = "23-45"
FLAVOR = "stream"  # Use "stream" for tables without visible borders.


def split_cell(value):
    """Split a cell containing one value per line, preserving blank entries."""
    if value is None:
        return []
    value = str(value)
    if not value.strip():
        return []
    return [line.strip() for line in value.splitlines()]


def extract_columnar_dump(df):
    """
    Recover a table when Camelot puts all headers in the first cell and
    each data column in a newline-separated cell.
    """
    if df.empty:
        return None

    first_row = [str(value).strip() for value in df.iloc[0].tolist()]
    # This format has multiple header lines in the first cell and otherwise
    # empty cells on the header row.
    if not first_row or len(first_row[0].splitlines()) < 2:
        return None
    if any(value for value in first_row[1:]):
        return None

    headers = [value.strip() for value in first_row[0].splitlines()]
    if len(df) < 2:
        raise ValueError("Found stacked headers, but no data row.")

    # The pasted output has one data row containing newline-separated columns.
    # If there are multiple data rows, combine each column's cells in order.
    columns = []
    for col_index in range(df.shape[1]):
        values = []
        for row_index in range(1, len(df)):
            values.extend(split_cell(df.iat[row_index, col_index]))
        columns.append(values)

    # Ignore trailing empty Camelot columns, but keep empty columns between
    # populated ones because they may represent real table fields.
    while columns and not columns[-1]:
        columns.pop()

    if len(headers) != len(columns):
        raise ValueError(
            f"Found {len(headers)} headers but {len(columns)} data columns. "
            "The PDF table may need different Camelot settings."
        )

    # Use the first populated column as the expected number of records.
    row_count = max((len(column) for column in columns), default=0)
    mismatches = [
        (headers[i], len(column))
        for i, column in enumerate(columns)
        if column and len(column) != row_count
    ]
    if mismatches:
        details = ", ".join(f"{name}: {count}" for name, count in mismatches)
        raise ValueError(
            f"Columns have inconsistent value counts (expected {row_count}): "
            f"{details}. Check the PDF extraction; wrapped text may need "
            "layout-specific handling."
        )

    rows = []
    for row_index in range(row_count):
        rows.append([
            columns[col_index][row_index] if columns[col_index] else ""
            for col_index in range(len(headers))
        ])

    return headers, rows


def extract_regular_table(df):
    """Use Camelot's cells directly when it has already found the table rows."""
    if df.empty:
        return None

    rows = [[str(value).strip() for value in row] for row in df.values.tolist()]
    # Camelot's first row is often the table header.
    headers = rows[0]
    return headers, rows[1:]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tables = camelot.read_pdf(
        str(PDF_PATH),
        pages=PAGES,
        flavor=FLAVOR,
    )
    print(f"Found {len(tables)} tables")

    for index, table in enumerate(tables, start=1):
        try:
            extracted = (
                extract_columnar_dump(table.df)
                or extract_regular_table(table.df)
            )
        except ValueError as error:
            print(f"Skipping page {table.page}, table {index}: {error}")
            continue

        if not extracted:
            print(f"Skipping empty table on page {table.page}")
            continue

        headers, rows = extracted
        output_path = OUTPUT_DIR / f"page_{table.page}_table_{index}.csv"

        with output_path.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows)

        print(f"Saved {output_path} ({len(rows)} data rows)")


if __name__ == "__main__":
    main()
