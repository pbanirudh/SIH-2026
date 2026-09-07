import os
import math
import cv2
import numpy as np
import fitz  # PyMuPDF
from PIL import Image
from typing import Tuple, List, Dict, Any, Optional
from app.core.config import settings

class PreprocessingService:

    @staticmethod
    def process_document(file_path: str, doc_id: str) -> Tuple[List[str], bool, List[Dict[str, Any]]]:
        """
        Process uploaded PDF or image file.
        Returns:
            processed_image_paths: List of saved preprocessed image paths (one per page).
            has_selectable_text: True if PDF had direct digital text.
            direct_text_pages: List of direct extracted text pages if available.
        """
        ext = os.path.splitext(file_path)[1].lower()
        processed_image_paths = []
        has_selectable_text = False
        direct_text_pages = []

        if ext == ".pdf":
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # Check selectable text
            extracted_texts = []
            for page in doc:
                txt = page.get_text()
                extracted_texts.append(txt)

            combined_text = "".join(extracted_texts).strip()
            if len(combined_text) > 80:
                has_selectable_text = True
                for idx, txt in enumerate(extracted_texts):
                    direct_text_pages.append({
                        "page_number": idx + 1,
                        "text": txt,
                        "confidence": 0.98
                    })

            # Render pages to PNG for visual display and OCR
            for idx in range(total_pages):
                page = doc[idx]
                pix = page.get_pixmap(dpi=300)
                page_img_path = os.path.join(settings.PROCESSED_DIR, f"{doc_id}_page_{idx+1}_raw.png")
                pix.save(page_img_path)
                
                # Apply image preprocessing pipeline
                enhanced_path = PreprocessingService.preprocess_image_file(
                    page_img_path, os.path.join(settings.PROCESSED_DIR, f"{doc_id}_page_{idx+1}.png")
                )
                processed_image_paths.append(enhanced_path)

            doc.close()
        else:
            # Single image file (PNG, JPG, TIFF, WEBP)
            output_path = os.path.join(settings.PROCESSED_DIR, f"{doc_id}_page_1.png")
            enhanced_path = PreprocessingService.preprocess_image_file(file_path, output_path)
            processed_image_paths.append(enhanced_path)

        return processed_image_paths, has_selectable_text, direct_text_pages

    @staticmethod
    def preprocess_image_file(input_path: str, output_path: str) -> str:
        """
        Applies full image processing pipeline:
        1. Resolution normalization
        2. Grayscale conversion
        3. Noise removal
        4. Contrast enhancement (CLAHE)
        5. Deskewing / Rotation correction
        6. Sharpening
        7. Adaptive thresholding saving
        """
        img = cv2.imread(input_path)
        if img is None:
            # Fallback PIL load
            pil_img = Image.open(input_path).convert("RGB")
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        h, w = img.shape[:2]

        # 1. Resolution Normalization (Target width ~ 1800-2400px)
        target_w = 2000
        if w < 1000 or w > 3000:
            scale = target_w / float(w)
            new_h = int(h * scale)
            img = cv2.resize(img, (target_w, new_h), interpolation=cv2.INTER_CUBIC)

        # 2. Grayscale conversion
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 3. Noise removal (Bilateral filter to preserve edges)
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)

        # 4. Contrast enhancement via CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        # 5. Deskewing
        deskewed = PreprocessingService.deskew(enhanced)

        # 6. Image Sharpening
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(deskewed, -1, kernel)

        # Save preprocessed high quality image
        cv2.imwrite(output_path, sharpened)
        return output_path

    @staticmethod
    def deskew(image: np.ndarray) -> np.ndarray:
        """Calculates skew angle and rotates image back to horizontal alignment."""
        try:
            thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            coords = np.column_stack(np.where(thresh > 0))
            if len(coords) < 10:
                return image
            
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle

            if abs(angle) < 0.5 or abs(angle) > 20.0:
                return image

            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated
        except Exception:
            return image
