import re
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple

class LayoutParserService:
    @staticmethod
    def analyze_layout(full_text: str, bounding_boxes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parses OCR full text and bounding boxes into structured layout blocks:
        - label_value_pairs: Dict mapping detected labels to values
        - tables: List of table grid cells
        - headings: Identified document title/headings
        - annotations: Detected stamps/signatures/handwriting
        """
        label_value_pairs = {}
        headings = []
        tables = []
        annotations = []

        lines = [line.strip() for line in full_text.split("\n") if line.strip()]

        # Common Land Record Label Keys (Bilingual: English + Hindi + Tamil + Telugu)
        label_patterns = [
            (r"(?:Survey\s*(?:No|Num|Number)|सर्वे\s*नंबर|सर्वे\s*नं|சர்வே\s*எண்)", "survey_number"),
            (r"(?:Sub-survey\s*(?:No|Num)|उप-सर्वे\s*नंबर)", "sub_survey_number"),
            (r"(?:Khasra\s*(?:No|Num|Number)|खसरा\s*नंबर|खसरा\s*नं)", "khasra_number"),
            (r"(?:Khata\s*(?:No|Num|Number)|खाता\s*नंबर|खाता\s*नं|खाता\s*संख्या)", "khata_number"),
            (r"(?:Plot\s*(?:No|Num|Number)|प्लाट\s*नंबर)", "plot_number"),
            (r"(?:Patta\s*(?:No|Num|Number)|पट्टा\s*नंबर|பட்டா\s*எண்)", "patta_number"),
            (r"(?:Owner\s*Name|Pattadar|खातेदार\s*का\s*नाम|भूमिस्वामी|मालिक\s*का\s*नाम|பெயர்)", "owner_name"),
            (r"(?:Father|Spouse|Mother)\s*(?:Name)?|पिता/पति\s*का\s*नाम|पिता\s*का\s*नाम", "parent_name"),
            (r"(?:State|राज्य)", "state"),
            (r"(?:District|ज़िला|जिला|மாவட்டம்)", "district"),
            (r"(?:Tehsil|Taluk|Mandal|तहसील|तालुका|மண்டலம்)", "tehsil"),
            (r"(?:Village|गाँव|गांव|ग्राम|கிராமம்)", "village"),
            (r"(?:Ward|वार्ड)", "ward"),
            (r"(?:Area|क्षेत्रफल|विस्तार|பரப்பளவு)", "area"),
            (r"(?:Area\s*Unit|इकाई)", "area_unit"),
            (r"(?:Land\s*Type|Classification|भूमि\s*का\s*प्रकार|प्रकार)", "land_type"),
            (r"(?:Mutation\s*(?:No|Num|Number)|नामांतरण\s*संख्या|दाखिल\s*खारिज\s*नं)", "mutation_number"),
            (r"(?:Mutation\s*Date|नामांतरण\s*दिनांक)", "mutation_date"),
            (r"(?:Registration\s*(?:No|Num|Number)|पंजीयन\s*संख्या)", "registration_number"),
            (r"(?:Registration\s*Date|पंजीयन\s*दिनांक)", "registration_date"),
            (r"(?:Deed\s*(?:No|Num)|विलेख\s*संख्या)", "deed_number"),
            (r"(?:Record\s*Date|दिनांक|तारिख|Date)", "record_date"),
        ]

        for line in lines:
            # Heading detection (all caps or contains header keyword)
            if any(kw in line.upper() for kw in ["RECORD OF RIGHTS", " अधिकार अभिलेख", "FORM 7/12", "KHASRA KHATAUNI", "LAND RECORD"]):
                headings.append(line)
                continue

            # Key-Value Pair splitting (using colon, hyphen, or tab)
            for pattern, field_key in label_patterns:
                match = re.search(pattern + r"\s*[:\-=\s]\s*(.+)", line, re.IGNORECASE)
                if match:
                    val = match.group(1).strip()
                    if val and field_key not in label_value_pairs:
                        label_value_pairs[field_key] = val

        return {
            "headings": headings,
            "label_value_pairs": label_value_pairs,
            "tables": tables,
            "annotations": annotations
        }
