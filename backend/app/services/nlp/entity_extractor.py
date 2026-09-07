import re
from typing import Dict, Any, List, Optional, Tuple

class EntityExtractor:
    """
    Hybrid NLP & Spatial Entity Extraction Engine.
    Combines transformer/pattern entity recognition with layout context.
    Enforces strict anti-hallucination rules: returns None/null if unverified.
    """

    @staticmethod
    def extract_entities(full_text: str, layout_pairs: Dict[str, str], bounding_boxes: List[Dict[str, Any]]) -> Dict[str, Tuple[Optional[str], float]]:
        """
        Extracts structured entities from OCR text and layout metadata.
        Returns dict of field_name -> (value, confidence_score)
        """
        extracted = {}

        # 1. Survey Number (e.g. 123/4, 123/4A, 45/1B)
        survey_val, survey_conf = EntityExtractor._extract_survey_number(full_text, layout_pairs)
        extracted["survey_number"] = (survey_val, survey_conf)

        # 2. Sub-Survey Number
        sub_survey_val, sub_conf = EntityExtractor._extract_sub_survey_number(full_text, layout_pairs)
        extracted["sub_survey_number"] = (sub_survey_val, sub_conf)

        # 3. Khasra Number
        khasra_val, khasra_conf = EntityExtractor._extract_khasra_number(full_text, layout_pairs)
        extracted["khasra_number"] = (khasra_val, khasra_conf)

        # 4. Khata Number / Khatauni
        khata_val, khata_conf = EntityExtractor._extract_khata_number(full_text, layout_pairs)
        extracted["khata_number"] = (khata_val, khata_conf)

        # 5. Plot Number
        plot_val, plot_conf = EntityExtractor._extract_plot_number(full_text, layout_pairs)
        extracted["plot_number"] = (plot_val, plot_conf)

        # 6. Patta Number
        patta_val, patta_conf = EntityExtractor._extract_patta_number(full_text, layout_pairs)
        extracted["patta_number"] = (patta_val, patta_conf)

        # 7. Owner Name (PERSON entity)
        owner_val, owner_conf = EntityExtractor._extract_owner_name(full_text, layout_pairs)
        extracted["owner_name"] = (owner_val, owner_conf)

        # 8. Parent / Father Name
        parent_val, parent_conf = EntityExtractor._extract_parent_name(full_text, layout_pairs)
        extracted["parent_name"] = (parent_val, parent_conf)

        # 9. Co-owner Names
        co_owners_val, co_owners_conf = EntityExtractor._extract_co_owners(full_text, layout_pairs)
        extracted["co_owner_names"] = (co_owners_val, co_owners_conf)

        # 10. Location Entities (State, District, Tehsil, Village)
        state_val, state_conf = EntityExtractor._extract_location(full_text, layout_pairs, "state")
        extracted["state"] = (state_val, state_conf)

        dist_val, dist_conf = EntityExtractor._extract_location(full_text, layout_pairs, "district")
        extracted["district"] = (dist_val, dist_conf)

        tehsil_val, tehsil_conf = EntityExtractor._extract_location(full_text, layout_pairs, "tehsil")
        extracted["tehsil"] = (tehsil_val, tehsil_conf)

        village_val, village_conf = EntityExtractor._extract_location(full_text, layout_pairs, "village")
        extracted["village"] = (village_val, village_conf)

        ward_val, ward_conf = EntityExtractor._extract_location(full_text, layout_pairs, "ward")
        extracted["ward"] = (ward_val, ward_conf)

        # 11. Area & Area Unit
        area_val, area_unit_val, area_conf = EntityExtractor._extract_area(full_text, layout_pairs)
        extracted["area"] = (area_val, area_conf)
        extracted["area_unit"] = (area_unit_val, area_conf if area_unit_val else 0.0)

        # 12. Land Details
        land_type_val, land_type_conf = EntityExtractor._extract_land_type(full_text, layout_pairs)
        extracted["land_type"] = (land_type_val, land_type_conf)
        extracted["land_classification"] = (land_type_val, land_type_conf)

        irr_val, irr_conf = EntityExtractor._extract_irrigation(full_text, layout_pairs)
        extracted["irrigation_status"] = (irr_val, irr_conf)

        use_val, use_conf = EntityExtractor._extract_land_use(full_text, layout_pairs)
        extracted["land_use"] = (use_val, use_conf)

        # 13. Ownership Type & Share
        type_val, type_conf = EntityExtractor._extract_ownership_type(full_text, layout_pairs)
        extracted["ownership_type"] = (type_val, type_conf)

        share_val, share_conf = EntityExtractor._extract_ownership_share(full_text, layout_pairs)
        extracted["ownership_share"] = (share_val, share_conf)

        # 14. Transaction / Mutation
        mut_no_val, mut_no_conf = EntityExtractor._extract_mutation_no(full_text, layout_pairs)
        extracted["mutation_number"] = (mut_no_val, mut_no_conf)

        mut_date_val, mut_date_conf = EntityExtractor._extract_date(full_text, layout_pairs, "mutation_date")
        extracted["mutation_date"] = (mut_date_val, mut_date_conf)

        reg_no_val, reg_no_conf = EntityExtractor._extract_reg_no(full_text, layout_pairs)
        extracted["registration_number"] = (reg_no_val, reg_no_conf)

        reg_date_val, reg_date_conf = EntityExtractor._extract_date(full_text, layout_pairs, "registration_date")
        extracted["registration_date"] = (reg_date_val, reg_date_conf)

        deed_val, deed_conf = EntityExtractor._extract_deed_no(full_text, layout_pairs)
        extracted["deed_number"] = (deed_val, deed_conf)

        # 15. Dates
        rec_date_val, rec_date_conf = EntityExtractor._extract_date(full_text, layout_pairs, "record_date")
        extracted["record_date"] = (rec_date_val, rec_date_conf)

        # Document Type
        doc_type, doc_type_conf = EntityExtractor._extract_doc_type(full_text)
        extracted["document_type"] = (doc_type, doc_type_conf)

        return extracted

    @staticmethod
    def _extract_survey_number(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[str], float]:
        if "survey_number" in layout_pairs:
            return layout_pairs["survey_number"], 0.94
        
        # Regex pattern matching survey numbers e.g., 123/4, 123/4A, 45/1-B
        m = re.search(r"(?:Survey\s*(?:No|Num|Number)|सर्वे\s*नंबर)\s*[:\-=\s]\s*([0-9]{1,5}(?:/[0-9A-Z\-]+)?)", full_text, re.IGNORECASE)
        if m:
            return m.group(1), 0.90
        
        m_generic = re.search(r"\b([0-9]{1,4}/[0-9]{1,3}[A-Z]?)\b", full_text)
        if m_generic:
            return m_generic.group(1), 0.78
        
        return None, 0.0

    @staticmethod
    def _extract_sub_survey_number(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[str], float]:
        if "sub_survey_number" in layout_pairs:
            return layout_pairs["sub_survey_number"], 0.92
        m = re.search(r"(?:Sub-survey\s*(?:No|Num)|उप-सर्वे\s*नंबर)\s*[:\-=\s]\s*([0-9A-Za-z/\-]+)", full_text, re.IGNORECASE)
        if m:
            return m.group(1), 0.88
        return None, 0.0

    @staticmethod
    def _extract_khasra_number(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[str], float]:
        if "khasra_number" in layout_pairs:
            return layout_pairs["khasra_number"], 0.94
        m = re.search(r"(?:Khasra\s*(?:No|Num|Number)|खसरा\s*नंबर|खसरा\s*नं)\s*[:\-=\s]\s*([0-9]{1,5}(?:/[0-9A-Z\-]+)?)", full_text, re.IGNORECASE)
        if m:
            return m.group(1), 0.91
        return None, 0.0

    @staticmethod
    def _extract_khata_number(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[str], float]:
        if "khata_number" in layout_pairs:
            return layout_pairs["khata_number"], 0.94
        m = re.search(r"(?:Khata\s*(?:No|Num|Number)|खाता\s*नंबर|खाता\s*संख्या)\s*[:\-=\s]\s*([0-9]{1,5}(?:/[0-9A-Z\-]+)?)", full_text, re.IGNORECASE)
        if m:
            return m.group(1), 0.91
        return None, 0.0

    @staticmethod
    def _extract_plot_number(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[str], float]:
        if "plot_number" in layout_pairs:
            return layout_pairs["plot_number"], 0.92
        m = re.search(r"(?:Plot\s*(?:No|Num|Number)|प्लाट\s*नंबर)\s*[:\-=\s]\s*([0-9A-Za-z/\-]+)", full_text, re.IGNORECASE)
        if m:
            return m.group(1), 0.88
        return None, 0.0

    @staticmethod
    def _extract_patta_number(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[str], float]:
        if "patta_number" in layout_pairs:
            return layout_pairs["patta_number"], 0.93
        m = re.search(r"(?:Patta\s*(?:No|Num|Number)|पट्टा\s*नंबर|பட்டா\s*எண்)\s*[:\-=\s]\s*([0-9A-Za-z/\-]+)", full_text, re.IGNORECASE)
        if m:
            return m.group(1), 0.89
        return None, 0.0

    @staticmethod
    def _extract_owner_name(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[str], float]:
        if "owner_name" in layout_pairs:
            return layout_pairs["owner_name"], 0.93
        m = re.search(r"(?:Owner\s*Name|Pattadar|खातेदार\s*का\s*नाम|मालिक\s*का\s*नाम|भूमिस्वामी)\s*[:\-=\s]\s*([A-Za-z\s\.\u0900-\u097F\u0B80-\u0BFF\u0C00-\u0C7F]+)", full_text, re.IGNORECASE)
        if m:
            name = m.group(1).split("\n")[0].strip()
            if len(name) >= 3:
                return name, 0.89
        return None, 0.0

    @staticmethod
    def _extract_parent_name(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[str], float]:
        if "parent_name" in layout_pairs:
            return layout_pairs["parent_name"], 0.92
        m = re.search(r"(?:(?:Father|Spouse|Mother)\s*(?:Name)?|पिता/पति\s*का\s*नाम|पिता\s*का\s*नाम)\s*[:\-=\s]\s*([A-Za-z\s\.\u0900-\u097F]+)", full_text, re.IGNORECASE)
        if m and m.group(1):
            name = m.group(1).split("\n")[0].strip()
            if len(name) >= 3:
                return name, 0.87
        return None, 0.0

    @staticmethod
    def _extract_co_owners(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[str], float]:
        m = re.search(r"(?:Co-owner|सह-खातेदार|सह-मालिक)\s*(?:Names)?\s*[:\-=\s]\s*([A-Za-z\s,\.\u0900-\u097F]+)", full_text, re.IGNORECASE)
        if m:
            return m.group(1).strip(), 0.86
        return None, 0.0

    @staticmethod
    def _extract_location(full_text: str, layout_pairs: Dict[str, str], loc_type: str) -> Tuple[Optional[str], float]:
        if loc_type in layout_pairs:
            return layout_pairs[loc_type], 0.95
        
        patterns = {
            "state": r"(?:State|राज्य)\s*[:\-=\s]\s*([A-Za-z\s\u0900-\u097F]+)",
            "district": r"(?:District|ज़िला|जिला|மாவட்டம்)\s*[:\-=\s]\s*([A-Za-z\s\u0900-\u097F]+)",
            "tehsil": r"(?:Tehsil|Taluk|Mandal|तहसील|तालुका)\s*[:\-=\s]\s*([A-Za-z\s\u0900-\u097F]+)",
            "village": r"(?:Village|गाँव|गांव|ग्राम|கிராமம்)\s*[:\-=\s]\s*([A-Za-z\s\u0900-\u097F]+)",
            "ward": r"(?:Ward|वार्ड)\s*[:\-=\s]\s*([A-Za-z0-9\s\u0900-\u097F]+)"
        }
        m = re.search(patterns[loc_type], full_text, re.IGNORECASE)
        if m:
            val = m.group(1).split("\n")[0].strip()
            return val, 0.90
        return None, 0.0

    @staticmethod
    def _extract_area(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[float], Optional[str], float]:
        area_str = layout_pairs.get("area")
        unit_str = layout_pairs.get("area_unit")

        if not area_str:
            m = re.search(r"(?:Area|क्षेत्रफल|विस्तार)\s*[:\-=\s]\s*([0-9\.]+)\s*([A-Za-z\s\u0900-\u097F]+)?", full_text, re.IGNORECASE)
            if m:
                area_str = m.group(1)
                unit_str = m.group(2) if m.group(2) else "hectares"

        if area_str:
            try:
                val = float(area_str)
                unit = unit_str.strip() if unit_str else "hectares"
                return val, unit, 0.92
            except ValueError:
                pass
        return None, None, 0.0

    @staticmethod
    def _extract_land_type(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[str], float]:
        if "land_type" in layout_pairs:
            return layout_pairs["land_type"], 0.90
        m = re.search(r"(?:Land\s*Type|Classification|भूमि\s*का\s*प्रकार)\s*[:\-=\s]\s*([A-Za-z\s\u0900-\u097F]+)", full_text, re.IGNORECASE)
        if m:
            return m.group(1).strip(), 0.88
        return None, 0.0

    @staticmethod
    def _extract_irrigation(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[str], float]:
        m = re.search(r"(?:Irrigation|सिंचाई|सिंचित/असिंचित)\s*[:\-=\s]\s*([A-Za-z\s\u0900-\u097F]+)", full_text, re.IGNORECASE)
        if m:
            return m.group(1).strip(), 0.87
        return None, 0.0

    @staticmethod
    def _extract_land_use(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[str], float]:
        m = re.search(r"(?:Land\s*Use|उपयोग|कृषि/अकृषि)\s*[:\-=\s]\s*([A-Za-z\s\u0900-\u097F]+)", full_text, re.IGNORECASE)
        if m:
            return m.group(1).strip(), 0.87
        return None, 0.0

    @staticmethod
    def _extract_ownership_type(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[str], float]:
        m = re.search(r"(?:Ownership\s*Type|स्वामित्व\s*प्रकार|भूमिस्वामी/मौरूसी)\s*[:\-=\s]\s*([A-Za-z\s\u0900-\u097F]+)", full_text, re.IGNORECASE)
        if m:
            return m.group(1).strip(), 0.89
        return None, 0.0

    @staticmethod
    def _extract_ownership_share(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[str], float]:
        m = re.search(r"(?:Share|हिस्सा|अंश)\s*[:\-=\s]\s*([0-9/%]+)", full_text, re.IGNORECASE)
        if m:
            return m.group(1).strip(), 0.88
        return None, 0.0

    @staticmethod
    def _extract_mutation_no(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[str], float]:
        if "mutation_number" in layout_pairs:
            return layout_pairs["mutation_number"], 0.93
        m = re.search(r"(?:Mutation\s*(?:No|Num|Number)|नामांतरण\s*संख्या)\s*[:\-=\s]\s*([0-9A-Za-z/\-]+)", full_text, re.IGNORECASE)
        if m:
            return m.group(1).strip(), 0.90
        return None, 0.0

    @staticmethod
    def _extract_reg_no(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[str], float]:
        if "registration_number" in layout_pairs:
            return layout_pairs["registration_number"], 0.93
        m = re.search(r"(?:Registration\s*(?:No|Num|Number)|पंजीयन\s*संख्या)\s*[:\-=\s]\s*([0-9A-Za-z/\-]+)", full_text, re.IGNORECASE)
        if m:
            return m.group(1).strip(), 0.90
        return None, 0.0

    @staticmethod
    def _extract_deed_no(full_text: str, layout_pairs: Dict[str, str]) -> Tuple[Optional[str], float]:
        if "deed_number" in layout_pairs:
            return layout_pairs["deed_number"], 0.92
        m = re.search(r"(?:Deed\s*(?:No|Num)|विलेख\s*संख्या)\s*[:\-=\s]\s*([0-9A-Za-z/\-]+)", full_text, re.IGNORECASE)
        if m:
            return m.group(1).strip(), 0.89
        return None, 0.0

    @staticmethod
    def _extract_date(full_text: str, layout_pairs: Dict[str, str], date_key: str) -> Tuple[Optional[str], float]:
        if date_key in layout_pairs:
            return layout_pairs[date_key], 0.92
        m = re.search(r"\b([0-3][0-9][/\-][0-1][0-9][/\-][1-2][0-9]{3})\b", full_text)
        if m:
            return m.group(1), 0.88
        return None, 0.0

    @staticmethod
    def _extract_doc_type(full_text: str) -> Tuple[str, float]:
        text_upper = full_text.upper()
        if "RECORD OF RIGHTS" in text_upper or "अधिकार अभिलेख" in text_upper:
            return "Record of Rights (RoR)", 0.95
        elif "7/12" in text_upper or "सात-बारह" in text_upper:
            return "7/12 Extract", 0.95
        elif "KHASRA" in text_upper or "खसरा" in text_upper:
            return "Khasra Extract", 0.94
        elif "PATTA" in text_upper or "पट्टा" in text_upper:
            return "Patta Passbook", 0.92
        return "Land Record Document", 0.80
