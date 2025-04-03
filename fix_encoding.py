import csv
import html

# Read the CSV file
with open('data/categories/keyword_based/Library_Usage.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Fix HTML entities in each field
for row in rows:
    for key in row:
        if row[key]:  # Only process non-empty fields
            row[key] = html.unescape(row[key])

# Write back to the same file
with open('data/categories/keyword_based/Library_Usage.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerows(rows) 