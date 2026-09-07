from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseOCREngine(ABC):
    @abstractmethod
    def process_image(self, image_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Process image file and return extracted text, confidence, bounding boxes, and structure.
        Returns:
            {
                "engine": str,
                "language": str,
                "full_text": str,
                "confidence": float,
                "bounding_boxes": [
                    {
                        "text": str,
                        "confidence": float,
                        "box": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],
                        "is_handwritten": bool
                    }
                ],
                "layout_elements": List[Dict]
            }
        """
        pass
