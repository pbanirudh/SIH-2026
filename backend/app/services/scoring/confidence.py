from typing import Tuple
from app.core.config import settings

class ConfidenceScoringEngine:
    @staticmethod
    def calculate_field_confidence(
        ocr_confidence: float,
        nlp_confidence: float,
        is_format_valid: bool = True,
        is_cross_field_valid: bool = True
    ) -> Tuple[float, str]:
        """
        Calculates composite confidence score [0.0 - 1.0] and categorizes into HIGH, MEDIUM, LOW.
        Weights:
        - OCR Confidence: 30%
        - NLP Confidence: 40%
        - Format Validity: 20%
        - Cross-field Consistency: 10%
        """
        if nlp_confidence == 0.0 or ocr_confidence == 0.0:
            format_weight = 0.5 if is_format_valid else 0.0
            score = (ocr_confidence * 0.3) + (nlp_confidence * 0.2) + format_weight
        else:
            fmt_score = 1.0 if is_format_valid else 0.2
            cross_score = 1.0 if is_cross_field_valid else 0.3
            score = (ocr_confidence * 0.30) + (nlp_confidence * 0.40) + (fmt_score * 0.20) + (cross_score * 0.10)

        final_score = round(min(max(score, 0.0), 1.0), 4)

        if final_score >= settings.CONFIDENCE_THRESHOLD_HIGH:
            category = "HIGH"
        elif final_score >= settings.CONFIDENCE_THRESHOLD_MEDIUM:
            category = "MEDIUM"
        else:
            category = "LOW"

        return final_score, category
