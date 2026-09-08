import os
from paddleocr import PaddleOCR
from document_parser import parse_document_ocr

print("[TEST] Initializing PaddleOCR...")
ocr = PaddleOCR(lang='en', ocr_version="PP-OCRv4", use_doc_orientation_classify=False, use_doc_unwarping=False)

samples = [
    ("RECORD OF RIGHTS", "test_images/sample_ror.png"),
    ("CONVEYANCE DEED", "test_images/sample_deed.png"),
    ("MUTATION ORDER", "test_images/sample_mutation.png"),
    ("CADASTRAL MAP", "test_images/sample_map.png"),
]

for title, path in samples:
    print(f"\n==========================================")
    print(f"[TEST] Processing {title} ({path})...")
    res = ocr.predict(path)
    lines = []
    if res:
        d = res[0].to_dict() if hasattr(res[0], 'to_dict') else res[0]
        lines = d.get("rec_texts") or d.get("rec_text") or []

    print(f"[TEST] Extracted {len(lines)} raw text lines.")
    parsed = parse_document_ocr(lines)
    print(f"[TEST] Classified Document Type: {parsed['classified_document_type']} (Confidence: {parsed['classification_confidence']:.2f})")
    print(f"[TEST] Structured Payload Keys: {list(parsed['structured_payload'].keys())}")
