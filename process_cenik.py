import pandas as pd
import re
import json
import unicodedata


def clean_text(s):
    if not s or pd.isna(s): return ""
    s = str(s)
    # Odstraní háčky a čárky
    s = "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return s.lower()


def tokenize(s):
    t = clean_text(s)
    # Vytáhne slova a čísla delší než 1 znak
    return re.findall(r'[a-z0-9]{2,}', t)


def process_demos_cenik(input_file, output_file):
    print(f"Načítám soubor: {input_file} ...")

    # Rozlišení mezi Excelem a CSV
    if input_file.endswith('.xlsx') or input_file.endswith('.xls'):
        # Pro Excel (.xlsx)
        df = pd.read_excel(input_file, header=None)
    else:
        # Pro CSV (pokus o Windows-1250 kódování, které Excel vyhazuje)
        try:
            df = pd.read_csv(input_file, sep=',', header=None, low_memory=False, encoding='cp1250')
        except:
            df = pd.read_csv(input_file, sep=';', header=None, low_memory=False, encoding='cp1250')

    clean_db = []

    for _, row in df.iterrows():
        # Kód je v prvním sloupci (index 0)
        code = str(row[0]).strip()
        # Název je v pátém sloupci (index 4)
        name = str(row[4]).strip()

        # Očista kódu (odstranění .0, pokud to Excel načetl jako float)
        if code.endswith('.0'):
            code = code[:-2]

        if code.isdigit() and len(code) >= 5 and name != "nan":
            thick_match = re.search(r'/(\d+)$', name)
            thick = thick_match.group(1) if thick_match else ""

            clean_db.append({
                "c": code,
                "n": name,
                "t": thick,
                "k": tokenize(name)
            })

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_db, f, ensure_ascii=False, separators=(',', ':'))

    print(f"Hotovo! Zpracováno {len(clean_db)} položek do souboru {output_file}")


# --- TADY SI ZMĚŇ NÁZEV SOUBORU ---
if __name__ == "__main__":
    process_demos_cenik('Export ceníku.xlsx', 'demos_db.json')