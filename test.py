# TVS_DND/test.py

from excel_handler import process_csv, export_cleaned_file
from dnd_api import upload_dnd_file


FILE_PATH = "sample.csv"

# Step 1 - Extract valid numbers
numbers = process_csv(FILE_PATH)

print("\nVALID MOBILE NUMBERS:\n")

for number in numbers:
    print(number)

print(f"\nTotal Valid Numbers: {len(numbers)}")

# Step 2 - Export cleaned file
if numbers:

    output_file = export_cleaned_file(numbers)

    print(f"\nOutput File: {output_file}")

    # Step 3 - Upload to DND API
    response = upload_dnd_file(output_file)

    print("\nFinal Response:")
    print(response)
