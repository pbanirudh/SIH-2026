"""
PaddleOCR Web Server & Document Intelligence Hub
================================================
Flask application serving:
1. Web UI for OCR processing & Synthetic Land Document Generation
2. REST API for OCR, document classification, & structured JSON extraction (4 schemas)
3. Synthetic Document Generator for RoR, Sale Deed, Mutation Order, & Cadastral Map
"""

import base64
import io
import json
import os
import sys
import tempfile
import time
import traceback

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request
from PIL import Image

# Local imports
from document_generator import (
    DEFAULT_DEED_PAYLOAD,
    DEFAULT_MAP_PAYLOAD,
    DEFAULT_MUTATION_PAYLOAD,
    DEFAULT_ROR_PAYLOAD,
    generate_document_image,
)
from document_parser import parse_document_ocr

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
PADDLEOCR_SRC = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "PaddleOCR-main",
    "PaddleOCR-main",
)
if os.path.isdir(PADDLEOCR_SRC) and PADDLEOCR_SRC not in sys.path:
    sys.path.insert(0, PADDLEOCR_SRC)

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB upload limit

# ---------------------------------------------------------------------------
# Lazy-loaded OCR engines
# ---------------------------------------------------------------------------
_ocr_engines: dict = {}


def get_ocr_engine(lang: str = "en"):
    """Return a cached PaddleOCR engine for the given language."""
    if lang not in _ocr_engines:
        print(f"[OCR] Initializing PaddleOCR engine for lang='{lang}' ...")
        from paddleocr import PaddleOCR

        kwargs = {
            "lang": lang,
            "use_doc_orientation_classify": False,
            "use_doc_unwarping": False,
        }
        # Specify version for English for optimal CPU compatibility
        if lang == "en":
            kwargs["ocr_version"] = "PP-OCRv4"

        engine = PaddleOCR(**kwargs)
        _ocr_engines[lang] = engine
        print(f"[OCR] Engine for lang='{lang}' ready.")
    return _ocr_engines[lang]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def draw_bounding_boxes(image_np: np.ndarray, results: list) -> np.ndarray:
    """Draw bounding boxes and text labels on the image."""
    annotated = image_np.copy()

    for item in results:
        box = item["box"]
        text = item["text"]
        conf = item["confidence"]

        if not box or len(box) == 0:
            continue

        pts = np.array(box, dtype=np.int32)

        # Color based on confidence
        if conf >= 0.9:
            color = (0, 200, 120)      # Bright Green
        elif conf >= 0.7:
            color = (0, 200, 255)      # Cyan/Yellow
        else:
            color = (0, 100, 255)      # Red-orange

        cv2.polylines(annotated, [pts], isClosed=True, color=color, thickness=2)

        if len(pts) > 0:
            x, y = int(pts[0][0]), int(pts[0][1])
            label = f"{text[:22]}{'...' if len(text) > 22 else ''} ({conf:.0%})"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            cv2.rectangle(annotated, (x, max(0, y - th - 8)), (x + tw + 6, max(th + 8, y)), color, -1)
            cv2.putText(
                annotated, label, (x + 3, max(th + 3, y - 4)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA,
            )

    return annotated


def pil_to_base64(pil_img: Image.Image) -> str:
    """Encode PIL Image to base64 PNG string."""
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def cv2_to_base64(image_np: np.ndarray) -> str:
    """Encode OpenCV BGR image to base64 PNG string."""
    rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    return pil_to_base64(pil_img)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/default_payloads", methods=["GET"])
def default_payloads():
    """Return preset sample payloads for all 4 document types."""
    return jsonify({
        "RECORD_OF_RIGHTS": DEFAULT_ROR_PAYLOAD,
        "CONVEYANCE_DEED": DEFAULT_DEED_PAYLOAD,
        "MUTATION_ORDER": DEFAULT_MUTATION_PAYLOAD,
        "CADASTRAL_MAP": DEFAULT_MAP_PAYLOAD,
    })


@app.route("/generate_doc", methods=["POST"])
def generate_doc_endpoint():
    """Generate synthetic land document image from type and optional custom JSON."""
    req_data = request.get_json(silent=True) or {}
    doc_type = req_data.get("doc_type", "RECORD_OF_RIGHTS")
    custom_payload = req_data.get("payload")

    try:
        pil_img = generate_document_image(doc_type, custom_payload)
        img_b64 = pil_to_base64(pil_img)

        return jsonify({
            "doc_type": doc_type,
            "image_base64": img_b64,
            "status": "success",
            "message": f"Generated synthetic document image for {doc_type}",
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/ocr", methods=["POST"])
def ocr_endpoint():
    """Accept image upload, run PaddleOCR, classify document, and extract structured JSON."""
    if "image" not in request.files:
        return jsonify({"error": "No image file uploaded."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    lang = request.form.get("lang", "en")

    suffix = os.path.splitext(file.filename)[1] or ".png"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        file.save(tmp.name)
        tmp.close()

        image_np = cv2.imread(tmp.name)
        if image_np is None:
            return jsonify({"error": "Could not decode image file."}), 400

        # Run PaddleOCR
        t0 = time.perf_counter()
        engine = get_ocr_engine(lang)
        raw_results = engine.predict(tmp.name)
        elapsed = time.perf_counter() - t0

        parsed = []
        raw_text_lines = []

        if raw_results:
            res = raw_results[0]
            d = res if isinstance(res, dict) else res.to_dict() if hasattr(res, 'to_dict') else {}

            texts = d.get("rec_texts") or d.get("rec_text") or []
            scores = d.get("rec_scores") or d.get("rec_score") or []
            boxes = d.get("dt_polys") or d.get("dt_poly") or d.get("rec_polys") or []

            for i in range(min(len(texts), len(scores))):
                text = str(texts[i]).strip()
                if not text:
                    continue
                score = float(scores[i])
                box = boxes[i].tolist() if i < len(boxes) and hasattr(boxes[i], 'tolist') else []
                parsed.append({
                    "text": text,
                    "confidence": round(score, 4),
                    "box": box,
                })
                raw_text_lines.append(text)

        # Document Classification & Structured Schema Extraction
        doc_analysis = parse_document_ocr(raw_text_lines)

        # Draw bounding boxes
        annotated_b64 = ""
        if parsed:
            annotated_img = draw_bounding_boxes(image_np, parsed)
            annotated_b64 = cv2_to_base64(annotated_img)

        return jsonify({
            "results": parsed,
            "annotated_image": annotated_b64,
            "processing_time": round(elapsed, 3),
            "language": lang,
            "total_lines": len(parsed),
            "classified_document_type": doc_analysis["classified_document_type"],
            "classification_confidence": doc_analysis["classification_confidence"],
            "structured_payload": doc_analysis["structured_payload"],
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("  PaddleOCR Land Document Intelligence Server starting...")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False)
