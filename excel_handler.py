# TVS_DND/excel_handler.py

import os
import re
import pandas as pd
import chardet

from datetime import datetime


def clean_mobile_number(mobile):
    """
    Cleans and validates mobile number.
    """

    if mobile is None:
        return None

    mobile = str(mobile).strip()

    # Keep only digits
    mobile = re.sub(r"\D", "", mobile)

    # Validate 10 digits
    if re.fullmatch(r"\d{10}", mobile):
        return mobile

    return None


def is_excel_file(file_path):
    """
    Detect if file is actually XLSX.
    """

    with open(file_path, "rb") as f:
        signature = f.read(2)

    return signature == b"PK"


def detect_encoding(file_path):

    with open(file_path, "rb") as f:
        raw_data = f.read(100000)

    result = chardet.detect(raw_data)

    encoding = result.get("encoding")

    if not encoding:
        encoding = "latin1"

    return encoding


def read_csv_safely(file_path):

    encodings_to_try = [
        detect_encoding(file_path),
        "utf-8",
        "latin1",
        "cp1252",
        "ISO-8859-1"
    ]

    for encoding in encodings_to_try:

        try:
            print(f"Trying CSV encoding: {encoding}")

            df = pd.read_csv(
                file_path,
                encoding=encoding,
                engine="python",
                on_bad_lines="skip"
            )

            print(f"Successfully read CSV with: {encoding}")

            return df

        except Exception as e:
            print(f"Failed encoding {encoding}: {e}")

    return None


def read_excel_safely(file_path):

    try:
        print("Detected XLSX file")

        df = pd.read_excel(
            file_path,
            engine="openpyxl"
        )

        print("Successfully read Excel file")

        return df

    except Exception as e:
        print(f"Excel read failed: {e}")
        return None


def process_csv(file_path):
    """
    Extract all valid unique mobile numbers.
    """

    # Detect actual file type
    if is_excel_file(file_path):
        df = read_excel_safely(file_path)
    else:
        df = read_csv_safely(file_path)

    if df is None:
        print("Unable to read input file.")
        return []

    # Normalize column names
    df.columns = [str(col).strip().upper() for col in df.columns]

    print("\nDetected Columns:")
    print(df.columns.tolist())

    # Validate required column
    if "MOBILE_NO" not in df.columns:
        print("Missing column: MOBILE_NO")
        return []

    valid_numbers = set()

    for _, row in df.iterrows():

        mobile = clean_mobile_number(row["MOBILE_NO"])

        if mobile:
            valid_numbers.add(mobile)

    return list(valid_numbers)


def export_cleaned_file(numbers):
    """
    Export cleaned numbers into processed CSV.
    """

    os.makedirs("processed", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_file = f"processed/cleaned_dnd_{timestamp}.csv"

    with open(output_file, "w") as f:

        for number in numbers:
            f.write(f"{number}\n")

    print(f"\nCleaned file generated: {output_file}")

    return output_file