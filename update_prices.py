import csv
import io
import re
from datetime import datetime
from pathlib import Path

import requests
from pypdf import PdfReader

FOD_PAGE_URL = "https://economie.fgov.be/nl/themas/energie/energieprijzen/maximumprijzen/officieel-tarief-van-de"
FOD_PDF_URL = "https://economie.fgov.be/sites/default/files/Files/Energy/prices/Officiele-Maximumtarieven-aardolieproducten.pdf"
CSV_PATH = Path("dataset.csv")

# Jouw bestaande dataset lijkt deze mapping te gebruiken:
# - Benzine 95   -> Benzine 95 RON E10 aan de pomp
# - Benzine 98   -> Benzine 98 RON E5 aan de pomp
# - Diesel       -> Diesel B7 aan de pomp
# - Stookolie    -> Gasolie vanaf 2000 l
TARGETS = {
    "Benzine 95": r"Benzine\s+95\s+RON\s+E10\s+aan\s+de\s+pomp\s+l\s+[0-9,().\-]+\s+21\s+([0-9]+(?:,[0-9]+)?)",
    "Benzine 98": r"Benzine\s+98\s+RON\s+E5\s+aan\s+de\s+pomp\s+l\s+[0-9,().\-]+\s+21\s+([0-9]+(?:,[0-9]+)?)",
    "Diesel": r"Diesel\s+B7\s+aan\s+de\s+pomp\s+l\s+[0-9,().\-]+\s+21\s+([0-9]+(?:,[0-9]+)?)",
    "Stookolie (bestelling > 2.000 liter)": r"Gasolie\s+vanaf\s+2000\s+l\s+l\s+[0-9,().\-]+\s+21\s+([0-9]+(?:,[0-9]+)?)",
}

def fetch_pdf_text() -> str:
    response = requests.get(FOD_PDF_URL, timeout=60)
    response.raise_for_status()
    pdf_bytes = io.BytesIO(response.content)
    reader = PdfReader(pdf_bytes)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if not text.strip():
        raise RuntimeError("Geen tekst uit de PDF kunnen halen.")
    return text

def parse_effective_date(pdf_text: str) -> str:
    match = re.search(r"geldig\s+vanaf\s*:\s*(\d{2}/\d{2}/\d{4})", pdf_text, re.IGNORECASE)
    if not match:
        raise RuntimeError("Geen geldigheidsdatum gevonden in de FOD-PDF.")
    dt = datetime.strptime(match.group(1), "%d/%m/%Y")
    return dt.strftime("%Y-%m-%d")

def parse_prices(pdf_text: str) -> dict:
    prices = {}
    for label, pattern in TARGETS.items():
        match = re.search(pattern, pdf_text, re.IGNORECASE)
        if not match:
            raise RuntimeError(f"Prijs voor '{label}' niet gevonden in de FOD-PDF.")
        prices[label] = float(match.group(1).replace(",", "."))
    return prices

def read_existing_rows():
    if not CSV_PATH.exists():
        return []
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows

def write_rows(rows):
    fieldnames = [
        "date",
        "Benzine 95",
        "Benzine 98",
        "Diesel",
        "Stookolie (bestelling > 2.000 liter)",
    ]
    rows_sorted = sorted(rows, key=lambda r: r["date"])
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows_sorted:
            writer.writerow(row)

def upsert_row(rows, new_row):
    by_date = {row["date"]: row for row in rows}
    by_date[new_row["date"]] = new_row
    return list(by_date.values())

def main():
    # Optionele ping naar de pagina zelf, zodat de action duidelijk faalt als de bronpagina weg is.
    page = requests.get(FOD_PAGE_URL, timeout=60)
    page.raise_for_status()

    pdf_text = fetch_pdf_text()
    effective_date = parse_effective_date(pdf_text)
    prices = parse_prices(pdf_text)

    rows = read_existing_rows()
    new_row = {"date": effective_date}
    for key, value in prices.items():
        new_row[key] = f"{value:.3f}"

    rows = upsert_row(rows, new_row)
    write_rows(rows)

    print("Bijgewerkt voor", effective_date, new_row)

if __name__ == "__main__":
    main()
