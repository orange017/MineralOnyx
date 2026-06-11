import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
import sqlite3
import os
from pathlib import Path

UPLOAD_DIR = str(Path("static", "uploads"))
DB_DILE = str(Path("instance", "stones.db"))
os.makedirs("static", exist_ok=True)
os.makedirs("instance", exist_ok=True)


NS = {
    "xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
}

def extract_images(xlsx_path: str, output_dir: str = UPLOAD_DIR):
    result = {}
    with zipfile.ZipFile(xlsx_path) as z:
        drawing = ET.fromstring(z.read("xl/drawings/drawing1.xml"))
        rels = ET.fromstring(z.read("xl/drawings/_rels/drawing1.xml.rels"))
        rid_to_target = {}
        for rel in rels:
            rid_to_target[rel.attrib["Id"]] = (rel.attrib["Target"])
        for anchor in drawing.findall("xdr:twoCellAnchor",NS):
            pic = anchor.find("xdr:pic", NS)
            if pic is None:
                continue
            row = int(anchor.find("xdr:from/xdr:row", NS).text) + 1
            blip = pic.find(".//a:blip", NS)
            rid = blip.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"]
            target = rid_to_target[rid]
            image_path = ("xl/" + target.replace("../", ""))
            image_name = os.path.basename(image_path)
            out_path = os.path.join(output_dir, image_name)
            with open(out_path, "wb") as fp:
                fp.write(z.read(image_path))
            result[row] = image_name
    return result

def export_to_sqlite(xlsx_path, sqlite_path = DB_DILE):
    df = pd.read_excel(xlsx_path)

    df = df.rename(columns={
        "Коллекционный номер": "collection_number",
        "Название образца": "sample_name",
        "Фотография": "photo",
        "Интересные факты": "facts",
        "Место отбора\\Кем доставлен": "source_location",
        "Стоимость": "cost",
        "Примерная Цена": "estimated_price"
    })

    # 2. Connect to SQLite
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    # 3. Pre-create the schema with a Primary Key
    cursor.execute("""CREATE TABLE IF NOT EXISTS stones (
            id INTEGER PRIMARY KEY,
            collection_number TEXT,
            sample_name TEXT,
            photo TEXT,
            facts TEXT,
            source_location TEXT,
            cost TEXT,
            estimated_price TEXT)""")
    conn.commit()

    row_to_image_mapping = extract_images(xlsx_path)
    df["photo"] = df.index.map(lambda idx: row_to_image_mapping.get(idx + 2))
    # df["id"] = df.index.map(lambda idx: idx)
    df.index.name = 'id'

    df.to_sql("stones", conn, if_exists="append", index=True)
    conn.close()

if __name__ == "__main__":
    export_to_sqlite("stones.xlsx")