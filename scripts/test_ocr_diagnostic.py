"""
Diagnostic: Run PaddleOCR on sample images and print the actual extracted text.
This reveals what text the OCR sees vs what the regex expects.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_ocr(image_path: str, lang: str = "en"):
    print(f"\n{'='*60}")
    print(f"Image: {os.path.basename(image_path)}")
    print(f"Language: {lang}")
    print('='*60)

    try:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang=lang, show_log=False)
        result = ocr.ocr(image_path, cls=True)
        
        if result and result[0]:
            full_lines = []
            for line in result[0]:
                text = line[1][0]
                conf = float(line[1][1])
                full_lines.append(text)
                print(f"  [{conf:.2f}] {text}")
            
            print(f"\n--- FULL TEXT ---")
            print("\n".join(full_lines))
        else:
            print("  No text detected by PaddleOCR!")
    except Exception as e:
        print(f"  PaddleOCR FAILED: {e}")
        print("  Trying pytesseract fallback...")
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            print(f"  Tesseract result:\n{text}")
        except Exception as e2:
            print(f"  Tesseract also failed: {e2}")

if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(__file__))
    samples = [
        ("sample_data/sample_land_record_en.png", "en"),
        ("sample_data/sample_land_record_hi.png", "hi"),
        ("sample_data/sample_land_record_ta.png", "ta"),
    ]
    for rel_path, lang in samples:
        full_path = os.path.join(base, rel_path)
        if os.path.exists(full_path):
            test_ocr(full_path, lang)
        else:
            print(f"NOT FOUND: {full_path}")
