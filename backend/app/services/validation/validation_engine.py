import re
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

class ValidationEngine:
    """
    Independent Validation Module enforcing format, logical, duplicate, and cross-field rules.
    Does NOT modify OCR/AI output silently; instead produces distinct validation status flags and warning logs.
    """

    @staticmethod
    def validate_record(record_data: Dict[str, Any], existing_records: List[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Validates extracted record fields.
        Returns:
            overall_validation_status: 'VALID', 'WARNING', 'INVALID'
            validation_issues: List of validation issue objects
        """
        issues = []

        # 1. Format Validations
        # Area numeric format
        area = record_data.get("area")
        if area is not None:
            if not isinstance(area, (int, float)) or area <= 0:
                issues.append({
                    "field_name": "area",
                    "rule_name": "positive_numeric_area",
                    "validation_type": "format",
                    "status": "INVALID",
                    "message": f"Area value '{area}' must be a positive number."
                })
            else:
                issues.append({
                    "field_name": "area",
                    "rule_name": "positive_numeric_area",
                    "validation_type": "format",
                    "status": "VALID",
                    "message": "Area is valid positive float."
                })

        # Date Format Check
        for date_field in ["mutation_date", "registration_date", "record_date"]:
            d_val = record_data.get(date_field)
            if d_val:
                is_valid_date = ValidationEngine._validate_date_format(d_val)
                if not is_valid_date:
                    issues.append({
                        "field_name": date_field,
                        "rule_name": "date_format_check",
                        "validation_type": "format",
                        "status": "WARNING",
                        "message": f"Date '{d_val}' does not conform to standard DD/MM/YYYY format."
                    })

        # Survey / Khasra Pattern Check
        survey = record_data.get("survey_number")
        khasra = record_data.get("khasra_number")
        if survey:
            if not re.match(r"^[0-9A-Za-z/\-\s]+$", str(survey)):
                issues.append({
                    "field_name": "survey_number",
                    "rule_name": "survey_pattern_check",
                    "validation_type": "format",
                    "status": "WARNING",
                    "message": f"Survey number '{survey}' contains unusual special characters."
                })

        # 2. Logical Validations
        # Ownership Share check (e.g. 50%, 1/2, 100%)
        share = record_data.get("ownership_share")
        if share:
            if "%" in share:
                try:
                    pct = float(share.replace("%", "").strip())
                    if pct > 100.0 or pct < 0.0:
                        issues.append({
                            "field_name": "ownership_share",
                            "rule_name": "share_percentage_boundary",
                            "validation_type": "logical",
                            "status": "INVALID",
                            "message": f"Ownership share percentage '{share}' exceeds 100%."
                        })
                except ValueError:
                    pass

        # 3. Cross-Field Validations
        # Required hierarchy: Village + District / Tehsil
        village = record_data.get("village")
        district = record_data.get("district")
        tehsil = record_data.get("tehsil")

        if village and not (district or tehsil):
            issues.append({
                "field_name": "village",
                "rule_name": "location_hierarchy_check",
                "validation_type": "cross_field",
                "status": "WARNING",
                "message": "Village specified without accompanying District or Tehsil location field."
            })

        # Village + Survey Number present check
        if not survey and not khasra and not record_data.get("plot_number"):
            issues.append({
                "field_name": "survey_number",
                "rule_name": "land_id_presence",
                "validation_type": "logical",
                "status": "WARNING",
                "message": "No land identifier (Survey / Khasra / Plot number) could be extracted."
            })

        # 4. Duplicate Detection Check
        if existing_records:
            cur_survey = str(survey or khasra or "").strip()
            cur_village = str(village or "").strip().lower()
            if cur_survey and cur_village:
                for rec in existing_records:
                    rec_surv = str(rec.get("survey_number") or rec.get("khasra_number") or "").strip()
                    rec_vill = str(rec.get("village") or "").strip().lower()
                    if rec_surv == cur_survey and rec_vill == cur_village:
                        issues.append({
                            "field_name": "survey_number",
                            "rule_name": "duplicate_record_check",
                            "validation_type": "duplicate",
                            "status": "WARNING",
                            "message": f"Potential duplicate record: Survey '{cur_survey}' in Village '{village}' already exists in database."
                        })
                        break

        # Compute overall record validation status
        has_invalid = any(i["status"] == "INVALID" for i in issues)
        has_warning = any(i["status"] == "WARNING" for i in issues)

        if has_invalid:
            overall_status = "INVALID"
        elif has_warning:
            overall_status = "WARNING"
        else:
            overall_status = "VALID"

        return overall_status, issues

    @staticmethod
    def _validate_date_format(date_str: str) -> bool:
        for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"]:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                if 1800 <= dt.year <= 2030:
                    return True
            except ValueError:
                continue
        return False
