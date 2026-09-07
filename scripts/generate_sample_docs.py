import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_fonts():
    """Loads clear system fonts with large sizes for readability."""
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 38)
        subtitle_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
        label_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 28)
        value_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 28)
        seal_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
        hand_font = ImageFont.truetype("C:/Windows/Fonts/ariali.ttf", 26)
    except Exception:
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 38)
            subtitle_font = ImageFont.truetype("arial.ttf", 24)
            label_font = ImageFont.truetype("arialbd.ttf", 28)
            value_font = ImageFont.truetype("arial.ttf", 28)
            seal_font = ImageFont.truetype("arialbd.ttf", 22)
            hand_font = ImageFont.truetype("ariali.ttf", 26)
        except Exception:
            title_font = subtitle_font = label_font = value_font = seal_font = hand_font = ImageFont.load_default()

    return title_font, subtitle_font, label_font, value_font, seal_font, hand_font

def create_synthetic_land_record(filename: str, language: str = "en"):
    """
    Creates high-resolution, crystal-clear synthetic land record image (PNG).
    Uses large 28-38px typography for maximum legibility.
    """
    width, height = 1600, 2200
    img = Image.new("RGB", (width, height), color=(252, 250, 242))
    draw = ImageDraw.Draw(img)

    title_font, subtitle_font, label_font, value_font, seal_font, hand_font = get_fonts()

    # Top Header Banner
    draw.rectangle([60, 50, width - 60, 180], fill=(224, 235, 248), outline=(20, 50, 120), width=4)
    
    if language == "hi":
        title = "REVENUE DEPARTMENT - RECORD OF RIGHTS (FORM 7/12)"
        sub_title = "Bilingual Land Record System (State of Uttar Pradesh / Hindi-English)"
        labels = [
            ("State (राज्य):", "Uttar Pradesh (उत्तर प्रदेश)"),
            ("District (ज़िला):", "Varanasi (वाराणसी)"),
            ("Tehsil (तहसील):", "Sadar (सदर)"),
            ("Village (गाँव):", "Rampur (रामपुर)"),
            ("Owner Name (खातेदार का नाम):", "Ramesh Kumar Sharma"),
            ("Father Name (पिता का नाम):", "Shyam Lal Sharma"),
            ("Survey Number (सर्वे नंबर):", "789/2A"),
            ("Khasra Number (खसरा नंबर):", "456/1B"),
            ("Khata Number (खाता नंबर):", "123/A"),
            ("Plot Number (प्लाट नंबर):", "PL-902"),
            ("Area (क्षेत्रफल):", "2.3500 hectares"),
            ("Land Classification (भूमि का प्रकार):", "Agricultural (कृषि)"),
            ("Irrigation Status (सिंचाई):", "Canal Irrigated (नहर)"),
            ("Mutation Number (नामांतरण संख्या):", "MUT-2024-8891"),
            ("Mutation Date (नामांतरण दिनांक):", "15/04/2024"),
            ("Registration Number (पंजीयन संख्या):", "REG-VAR-99120"),
            ("Record Date (अभिलेख दिनांक):", "07/09/2026"),
        ]
    elif language == "ta":
        title = "REVENUE DEPARTMENT - LAND RECORD (PATTA / CHITTA PASSBOOK)"
        sub_title = "State Revenue Department - Tamil Nadu Land Record (Synthetic)"
        labels = [
            ("State:", "Tamil Nadu"),
            ("District:", "Coimbatore"),
            ("Taluk:", "Pollachi"),
            ("Village:", "Anaimalai"),
            ("Owner / Pattadar Name:", "Murugan K"),
            ("Father / Spouse Name:", "Kandasamy"),
            ("Survey Number:", "123/4A"),
            ("Sub-survey Number:", "123/4A-1"),
            ("Patta Number:", "882"),
            ("Parcel ID:", "TN-CBE-88192"),
            ("Area:", "1.4500 hectares"),
            ("Area Unit:", "hectares"),
            ("Land Classification:", "Wet Agricultural Land"),
            ("Irrigation Status:", "River / Well Irrigated"),
            ("Mutation Number:", "MUT-TN-2025-01"),
            ("Mutation Date:", "10/01/2025"),
            ("Record Date:", "07/09/2026"),
        ]
    else:
        title = "GOVERNMENT OF MAHARASHTRA - RECORD OF RIGHTS (FORM 7/12)"
        sub_title = "National Land Digitization Authority (Official Sample Extract)"
        labels = [
            ("State:", "Maharashtra"),
            ("District:", "Pune"),
            ("Tehsil / Taluk:", "Haveli"),
            ("Village:", "Wagholi"),
            ("Ward / Locality:", "Ward No 4"),
            ("Owner Name:", "Ramesh Kumar Sharma"),
            ("Co-Owner Names:", "Suresh Kumar, Anita Sharma"),
            ("Father / Spouse Name:", "Shyam Lal Sharma"),
            ("Ownership Type:", "Occupant Class 1 (Bhumiswami)"),
            ("Ownership Share:", "100% (Single Holder)"),
            ("Survey Number:", "123/4"),
            ("Sub-survey Number:", "123/4A"),
            ("Khata Number:", "78/B"),
            ("Plot Number:", "PL-204"),
            ("Area:", "3.5000"),
            ("Area Unit:", "hectares"),
            ("Land Classification:", "Dry Agricultural (Jirayat)"),
            ("Irrigation Status:", "Well Irrigated"),
            ("Mutation Number:", "MUT-9921/2024"),
            ("Mutation Date:", "12/03/2024"),
            ("Registration Number:", "REG-88219/PN"),
            ("Record Date:", "07/09/2026"),
        ]

    # Draw Header Text
    draw.text((90, 70), title, fill=(15, 30, 80), font=title_font)
    draw.text((90, 125), sub_title, fill=(60, 60, 70), font=subtitle_font)

    # Main Data Table Box
    table_top = 220
    row_height = 70
    table_bottom = table_top + len(labels) * row_height + 20
    draw.rectangle([80, table_top, width - 80, table_bottom], outline=(30, 30, 30), width=3)
    draw.rectangle([80, table_top, width - 80, table_top + 50], fill=(235, 240, 248), outline=(30, 30, 30), width=2)
    draw.text((100, table_top + 10), "LAND RECORD ATTRIBUTES", fill=(20, 40, 90), font=label_font)
    draw.text((650, table_top + 10), "EXTRACTED VALUES", fill=(20, 40, 90), font=label_font)

    y = table_top + 60
    for label, val in labels:
        # Alternating background row shading
        if ((y - table_top) // row_height) % 2 == 1:
            draw.rectangle([82, y - 5, width - 82, y + row_height - 10], fill=(245, 247, 252))

        draw.text((100, y), label, fill=(30, 30, 30), font=label_font)
        draw.text((650, y), val, fill=(10, 40, 160), font=value_font)
        draw.line([(80, y + row_height - 10), (width - 80, y + row_height - 10)], fill=(210, 210, 210), width=1)
        y += row_height

    # Divider line down middle of table
    draw.line([(620, table_top + 50), (620, table_bottom)], fill=(180, 180, 180), width=2)

    # Official Seal
    seal_x, seal_y = width - 260, table_bottom - 220
    draw.ellipse([seal_x - 120, seal_y - 120, seal_x + 120, seal_y + 120], outline=(190, 30, 30), width=5)
    draw.ellipse([seal_x - 105, seal_y - 105, seal_x + 105, seal_y + 105], outline=(190, 30, 30), width=2)
    draw.text((seal_x - 90, seal_y - 25), "OFFICIAL SEAL\nREVENUE OFFICE", fill=(190, 30, 30), font=seal_font)

    # Handwriting Annotation
    draw.text((100, table_bottom + 30), "Handwritten Officer Note: Inspected & Verified by Revenue Officer on 07/09/2026", fill=(0, 110, 30), font=hand_font)
    draw.line([(100, table_bottom + 70), (1050, table_bottom + 70)], fill=(0, 110, 30), width=2)

    output_path = os.path.join(OUTPUT_DIR, filename)
    img.save(output_path)
    print(f"Generated high-resolution sample document ({width}x{height}): {output_path}")
    return output_path

if __name__ == "__main__":
    create_synthetic_land_record("sample_land_record_en.png", "en")
    create_synthetic_land_record("sample_land_record_hi.png", "hi")
    create_synthetic_land_record("sample_land_record_ta.png", "ta")
