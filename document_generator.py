"""
Indian Land Document Image Generator
====================================
Generates official synthetic document images corresponding to 4 standard land record schemas:
1. Record of Rights (RoR / Patta / 7/12 / Jamabandi / Khatauni)
2. Conveyance & Transfer Deeds (Sale Deed)
3. Mutation Register & Orders (Dakhil-Kharij / VF-6)
4. Spatial Cadastral Map (Bhu-Naksha / FMB)
"""

import io
import math
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def _get_font(size=16, bold=False):
    """Load default font fallback cleanly across OS platforms."""
    try:
        font_name = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(font_name, size)
    except IOError:
        try:
            font_name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
            return ImageFont.truetype(font_name, size)
        except IOError:
            return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Default Sample Data Payloads
# ---------------------------------------------------------------------------

DEFAULT_ROR_PAYLOAD = {
    "khata_number": "489",
    "parcels": [
        {
            "khasra_survey_number": "142/3B",
            "base_survey_no": "142",
            "sub_division": "3B",
            "bhu_aadhaar_ulpin": "14BW89201L9842",
            "plot_area": {
                "raw_recorded": "0.45 Acre",
                "metric_sqm": 1821.08,
                "metric_hectares": 0.1821
            },
            "land_classification": "Agricultural",
            "soil_type": "Wet / Nanja",
            "irrigation_source": "Government Canal"
        }
    ],
    "ownership_details": [
        {
            "owner_name": "K. Raman",
            "relationship_type": "Son of",
            "relative_name": "M. Murugan",
            "share_fraction": 1.0,
            "is_primary_owner": True
        }
    ],
    "revenue_taxation": {
        "annual_assessment_inr": 85.50,
        "cess_amount_inr": 12.00,
        "tax_status": "PAID"
    },
    "remarks_kaifiyat": "Bank loan lien active under SBI branch ref 2022/441"
}

DEFAULT_DEED_PAYLOAD = {
    "registration_details": {
        "deed_type": "SALE_DEED",
        "registration_number": "984/2021",
        "book_volume": "1",
        "page_range": "105-112",
        "sro_office": "Sriperumbudur SRO",
        "execution_date": "2021-04-12",
        "registration_date": "2021-04-14"
    },
    "parties": {
        "executants_sellers": [
            {
                "name": "M. Murugan",
                "relationship_type": "Son of",
                "relative_name": "K. Munusamy",
                "address": "No 12, Car Street, Nemili",
                "identifier_ref": "[Redacted]"
            }
        ],
        "claimants_buyers": [
            {
                "name": "K. Raman",
                "relationship_type": "Son of",
                "relative_name": "M. Murugan",
                "address": "No 14, East Mada Street, Nemili",
                "identifier_ref": "[Redacted]"
            }
        ]
    },
    "financial_consideration": {
        "sale_value_inr": 1500000.00,
        "guideline_value_inr": 1420000.00,
        "stamp_duty_paid_inr": 105000.00,
        "registration_fee_inr": 60000.00
    },
    "property_schedule": {
        "survey_number": "142/3B",
        "transacted_area_sqm": 1821.08,
        "four_boundaries_chauhaddi": {
            "north": "Survey No 141 (Public Canal)",
            "south": "Village Panchayat Road",
            "east": "Survey No 142/3A (P. Sundaram Land)",
            "west": "Survey No 143 (Village Commons)"
        }
    },
    "prior_title_recitals": "Vendor acquired rights via registered Settlement Deed No. 312/1998."
}

DEFAULT_MUTATION_PAYLOAD = {
    "mutation_serial_number": "MUT-2024-0012",
    "case_reference_no": "REV/TEH/2024/782",
    "nature_of_mutation": "SUCCESSION_INHERITANCE",
    "applied_date": "2024-01-10",
    "sanctioned_date": "2024-02-18",
    "survey_numbers_affected": ["142/3B"],
    "transferor_prior_owner": {
        "name": "M. Murugan",
        "prior_khata_no": "310"
    },
    "transferee_new_owner": {
        "name": "K. Raman",
        "new_khata_no": "489",
        "share_acquired": 1.0
    },
    "sanctioning_authority": {
        "officer_designation": "Tehsildar",
        "subdivision": "Sriperumbudur",
        "digital_signature_verified": True
    }
}

DEFAULT_MAP_PAYLOAD = {
    "map_sheet_number": "Sheet-04",
    "projection_system": "EPSG:4326",
    "extracted_features": [
        {
            "khasra_survey_number": "142/3B",
            "geometry_type": "Polygon",
            "coordinates": [
                [
                    [79.94125, 12.98142],
                    [79.94189, 12.98145],
                    [79.94185, 12.98082],
                    [79.94121, 12.98080],
                    [79.94125, 12.98142]
                ]
            ],
            "calculated_gis_area_sqm": 1821.50,
            "centroid": {
                "latitude": 12.98112,
                "longitude": 79.94155
            }
        }
    ],
    "tie_line_measurements": [
        {
            "from_marker": "G1",
            "to_marker": "G2",
            "field_distance_meters": 45.2
        }
    ]
}


# ---------------------------------------------------------------------------
# Generator Functions
# ---------------------------------------------------------------------------

def generate_ror_image(data=None) -> Image.Image:
    """Generate Record of Rights (RoR / Patta / 7/12) document image."""
    data = data or DEFAULT_ROR_PAYLOAD
    img = Image.new("RGB", (1000, 1300), color=(252, 252, 248))
    draw = ImageDraw.Draw(img)

    f_title = _get_font(22, bold=True)
    f_sub = _get_font(16, bold=True)
    f_label = _get_font(13, bold=True)
    f_text = _get_font(13, bold=False)

    # Outer border
    draw.rectangle([20, 20, 980, 1280], outline=(40, 40, 40), width=3)
    draw.rectangle([26, 26, 974, 1274], outline=(120, 120, 120), width=1)

    # Government Header
    draw.text((500, 60), "GOVERNMENT OF TAMIL NADU - REVENUE DEPARTMENT", fill=(10, 30, 80), font=f_sub, anchor="mm")
    draw.text((500, 95), "RECORD OF RIGHTS (RoR) / PATTA PASSBOOK", fill=(180, 20, 20), font=f_title, anchor="mm")
    draw.line([50, 120, 950, 120], fill=(40, 40, 40), width=2)

    # Khata & ULPIN Summary Box
    khata_no = data.get("khata_number", "489")
    parcel = data.get("parcels", [{}])[0]
    survey_no = parcel.get("khasra_survey_number", "142/3B")
    ulpin = parcel.get("bhu_aadhaar_ulpin", "14BW89201L9842")

    draw.rectangle([50, 140, 950, 210], fill=(240, 244, 250), outline=(100, 120, 160), width=2)
    draw.text((70, 160), f"KHATA NUMBER: {khata_no}", fill=(0, 0, 0), font=f_sub)
    draw.text((450, 160), f"SURVEY / KHASRA NO: {survey_no}", fill=(0, 0, 0), font=f_sub)
    draw.text((70, 185), f"BHU-AADHAAR ULPIN: {ulpin}", fill=(20, 80, 160), font=f_sub)

    # Table 1: Parcel & Land Particulars
    draw.text((50, 235), "1. PARCEL & LAND PARTICULARS", fill=(10, 30, 80), font=f_sub)
    
    table_top = 260
    table_bottom = 430
    draw.rectangle([50, table_top, 950, table_bottom], outline=(60, 60, 60), width=2)

    # Table grid headers
    cols = [50, 200, 350, 500, 650, 800, 950]
    headers = ["Survey No", "Base Survey", "Sub-Division", "Plot Area", "Land Class", "Soil Type"]
    draw.rectangle([50, table_top, 950, table_top + 35], fill=(220, 230, 242))
    for i in range(len(headers)):
        draw.line([cols[i], table_top, cols[i], table_bottom], fill=(60, 60, 60), width=1)
        draw.text(((cols[i] + cols[i+1])//2, table_top + 17), headers[i], fill=(0, 0, 0), font=f_label, anchor="mm")
    draw.line([cols[-1], table_top, cols[-1], table_bottom], fill=(60, 60, 60), width=1)
    draw.line([50, table_top + 35, 950, table_top + 35], fill=(60, 60, 60), width=2)

    # Table row values
    area_info = parcel.get("plot_area", {})
    area_str = f"{area_info.get('raw_recorded', '0.45 Acre')} ({area_info.get('metric_sqm', 1821.08)} sqm)"
    row_vals = [
        parcel.get("khasra_survey_number", "142/3B"),
        parcel.get("base_survey_no", "142"),
        parcel.get("sub_division", "3B"),
        area_str,
        parcel.get("land_classification", "Agricultural"),
        parcel.get("soil_type", "Wet / Nanja")
    ]
    for i in range(len(row_vals)):
        draw.text(((cols[i] + cols[i+1])//2, table_top + 60), str(row_vals[i]), fill=(20, 20, 20), font=f_text, anchor="mm")

    # Irrigation info line
    draw.text((70, 395), f"Irrigation Source: {parcel.get('irrigation_source', 'Government Canal')}", fill=(40, 40, 40), font=f_text)

    # Table 2: Ownership Details
    draw.text((50, 460), "2. REGISTERED OWNERSHIP DETAILS", fill=(10, 30, 80), font=f_sub)
    draw.rectangle([50, 490, 950, 620], outline=(60, 60, 60), width=2)

    cols_o = [50, 300, 500, 700, 950]
    headers_o = ["Owner Name", "Relationship", "Relative Name", "Share Fraction"]
    draw.rectangle([50, 490, 950, 525], fill=(220, 230, 242))
    for i in range(len(headers_o)):
        draw.line([cols_o[i], 490, cols_o[i], 620], fill=(60, 60, 60), width=1)
        draw.text(((cols_o[i] + cols_o[i+1])//2, 507), headers_o[i], fill=(0, 0, 0), font=f_label, anchor="mm")
    draw.line([cols_o[-1], 490, cols_o[-1], 620], fill=(60, 60, 60), width=1)
    draw.line([50, 525, 950, 525], fill=(60, 60, 60), width=2)

    owner = data.get("ownership_details", [{}])[0]
    row_o = [
        owner.get("owner_name", "K. Raman"),
        owner.get("relationship_type", "Son of"),
        owner.get("relative_name", "M. Murugan"),
        f"{owner.get('share_fraction', 1.0) * 100:.0f}% (Primary Owner)"
    ]
    for i in range(len(row_o)):
        draw.text(((cols_o[i] + cols_o[i+1])//2, 560), str(row_o[i]), fill=(20, 20, 20), font=f_text, anchor="mm")

    # Table 3: Revenue & Taxation
    draw.text((50, 650), "3. REVENUE ASSESSMENT & TAXATION", fill=(10, 30, 80), font=f_sub)
    tax = data.get("revenue_taxation", {})
    draw.rectangle([50, 680, 950, 770], fill=(250, 250, 245), outline=(60, 60, 60), width=1)
    draw.text((70, 700), f"Annual Assessment: INR {tax.get('annual_assessment_inr', 85.50):.2f}", fill=(0, 0, 0), font=f_text)
    draw.text((400, 700), f"Cess Amount: INR {tax.get('cess_amount_inr', 12.00):.2f}", fill=(0, 0, 0), font=f_text)
    draw.text((700, 700), f"Tax Status: {tax.get('tax_status', 'PAID')}", fill=(0, 140, 40), font=f_label)

    # Table 4: Remarks / Kaifiyat
    draw.text((50, 800), "4. REMARKS & ENCUMBRANCES (KAIFIYAT)", fill=(10, 30, 80), font=f_sub)
    remarks = data.get("remarks_kaifiyat", "Bank loan lien active under SBI branch ref 2022/441")
    draw.rectangle([50, 830, 950, 930], fill=(255, 245, 240), outline=(200, 100, 100), width=2)
    draw.text((70, 860), f"REMARKS: {remarks}", fill=(160, 20, 20), font=f_label)

    # Footer Seal & Signature
    draw.line([50, 1150, 950, 1150], fill=(150, 150, 150), width=1)
    draw.text((100, 1180), "Digitally Verified Record", fill=(100, 100, 100), font=f_text)
    draw.text((100, 1205), "Revenue Department Tamil Nadu", fill=(100, 100, 100), font=f_text)
    draw.text((700, 1180), "Tahsildar / Authorized Signatory", fill=(0, 0, 0), font=f_label)
    draw.text((700, 1205), "Sriperumbudur Taluk", fill=(0, 0, 0), font=f_text)

    return img


def generate_deed_image(data=None) -> Image.Image:
    """Generate Conveyance & Transfer Deed (Sale Deed) document image."""
    data = data or DEFAULT_DEED_PAYLOAD
    img = Image.new("RGB", (1000, 1400), color=(253, 251, 245))
    draw = ImageDraw.Draw(img)

    f_stamp = _get_font(20, bold=True)
    f_title = _get_font(22, bold=True)
    f_sub = _get_font(15, bold=True)
    f_label = _get_font(13, bold=True)
    f_text = _get_font(13, bold=False)

    # Stamp Paper Banner
    draw.rectangle([30, 30, 970, 160], fill=(245, 235, 210), outline=(180, 140, 60), width=3)
    draw.text((500, 60), "INDIA NON JUDICIAL", fill=(120, 40, 20), font=f_stamp, anchor="mm")
    draw.text((500, 95), "GOVERNMENT OF TAMIL NADU - STAMP DUTY RS. 100", fill=(140, 50, 20), font=f_sub, anchor="mm")
    draw.text((500, 130), "STAMP PAPER REF: TN-STMP-2021-984210", fill=(80, 80, 80), font=f_text, anchor="mm")

    # Document Header
    reg = data.get("registration_details", {})
    draw.text((500, 195), f"DEED OF ABSOLUTE SALE ({reg.get('deed_type', 'SALE_DEED')})", fill=(10, 20, 60), font=f_title, anchor="mm")
    draw.text((500, 225), f"Document No: {reg.get('registration_number', '984/2021')} | SRO: {reg.get('sro_office', 'Sriperumbudur SRO')}", fill=(60, 60, 60), font=f_sub, anchor="mm")
    draw.line([50, 250, 950, 250], fill=(40, 40, 40), width=2)

    # Section 1: Registration Details Box
    draw.rectangle([50, 270, 950, 350], fill=(245, 248, 252), outline=(100, 120, 150), width=1)
    draw.text((70, 285), f"Execution Date: {reg.get('execution_date', '2021-04-12')}", fill=(0, 0, 0), font=f_text)
    draw.text((500, 285), f"Registration Date: {reg.get('registration_date', '2021-04-14')}", fill=(0, 0, 0), font=f_text)
    draw.text((70, 315), f"Book Volume: {reg.get('book_volume', '1')}", fill=(0, 0, 0), font=f_text)
    draw.text((500, 315), f"Page Range: {reg.get('page_range', '105-112')}", fill=(0, 0, 0), font=f_text)

    # Section 2: Parties Involved
    draw.text((50, 380), "PARTIES TO THE CONVEYANCE DEED", fill=(10, 30, 80), font=f_sub)
    parties = data.get("parties", {})

    # Seller Box
    seller = parties.get("executants_sellers", [{}])[0]
    draw.rectangle([50, 410, 480, 520], fill=(255, 255, 255), outline=(160, 160, 160), width=1)
    draw.text((70, 425), "EXECUTANT / SELLER (VENDOR):", fill=(180, 30, 30), font=f_label)
    draw.text((70, 450), f"Name: {seller.get('name', 'M. Murugan')}", fill=(0, 0, 0), font=f_text)
    draw.text((70, 475), f"Relation: {seller.get('relationship_type', 'Son of')} {seller.get('relative_name', 'K. Munusamy')}", fill=(0, 0, 0), font=f_text)
    draw.text((70, 500), f"Address: {seller.get('address', 'Nemili')}", fill=(60, 60, 60), font=f_text)

    # Buyer Box
    buyer = parties.get("claimants_buyers", [{}])[0]
    draw.rectangle([520, 410, 950, 520], fill=(255, 255, 255), outline=(160, 160, 160), width=1)
    draw.text((540, 425), "CLAIMANT / BUYER (PURCHASER):", fill=(20, 140, 40), font=f_label)
    draw.text((540, 450), f"Name: {buyer.get('name', 'K. Raman')}", fill=(0, 0, 0), font=f_text)
    draw.text((540, 475), f"Relation: {buyer.get('relationship_type', 'Son of')} {buyer.get('relative_name', 'M. Murugan')}", fill=(0, 0, 0), font=f_text)
    draw.text((540, 500), f"Address: {buyer.get('address', 'Nemili')}", fill=(60, 60, 60), font=f_text)

    # Section 3: Financial Consideration
    draw.text((50, 550), "FINANCIAL CONSIDERATION & STAMP FEES", fill=(10, 30, 80), font=f_sub)
    fin = data.get("financial_consideration", {})
    draw.rectangle([50, 580, 950, 670], fill=(245, 250, 245), outline=(100, 160, 100), width=1)
    draw.text((70, 600), f"Total Sale Value: INR {fin.get('sale_value_inr', 1500000.0):,.2f}", fill=(0, 0, 0), font=f_label)
    draw.text((500, 600), f"Guideline Value: INR {fin.get('guideline_value_inr', 1420000.0):,.2f}", fill=(0, 0, 0), font=f_text)
    draw.text((70, 635), f"Stamp Duty Paid: INR {fin.get('stamp_duty_paid_inr', 105000.0):,.2f}", fill=(0, 0, 0), font=f_text)
    draw.text((500, 635), f"Registration Fee: INR {fin.get('registration_fee_inr', 60000.0):,.2f}", fill=(0, 0, 0), font=f_text)

    # Section 4: Property Schedule & Four Boundaries
    draw.text((50, 700), "PROPERTY SCHEDULE & FOUR BOUNDARIES (CHAUHADDI)", fill=(10, 30, 80), font=f_sub)
    prop = data.get("property_schedule", {})
    bounds = prop.get("four_boundaries_chauhaddi", {})

    draw.rectangle([50, 730, 950, 930], fill=(255, 255, 255), outline=(60, 60, 60), width=2)
    draw.text((70, 750), f"Transacted Survey Number: {prop.get('survey_number', '142/3B')}", fill=(0, 0, 0), font=f_label)
    draw.text((500, 750), f"Transacted Area: {prop.get('transacted_area_sqm', 1821.08)} sq. meters", fill=(0, 0, 0), font=f_label)

    draw.line([70, 780, 930, 780], fill=(200, 200, 200), width=1)
    draw.text((70, 795), f"NORTH: {bounds.get('north', 'Survey No 141 (Public Canal)')}", fill=(40, 40, 40), font=f_text)
    draw.text((70, 825), f"SOUTH: {bounds.get('south', 'Village Panchayat Road')}", fill=(40, 40, 40), font=f_text)
    draw.text((70, 855), f"EAST:  {bounds.get('east', 'Survey No 142/3A (P. Sundaram Land)')}", fill=(40, 40, 40), font=f_text)
    draw.text((70, 885), f"WEST:  {bounds.get('west', 'Survey No 143 (Village Commons)')}", fill=(40, 40, 40), font=f_text)

    # Section 5: Prior Title Recitals
    draw.text((50, 960), "PRIOR TITLE RECITALS", fill=(10, 30, 80), font=f_sub)
    recital = data.get("prior_title_recitals", "Vendor acquired rights via registered Settlement Deed No. 312/1998.")
    draw.rectangle([50, 990, 950, 1070], fill=(250, 250, 250), outline=(180, 180, 180), width=1)
    draw.text((70, 1020), recital, fill=(40, 40, 40), font=f_text)

    # Signatures
    draw.line([50, 1260, 950, 1260], fill=(150, 150, 150), width=1)
    draw.text((100, 1290), "Signature of Executant (Seller)", fill=(0, 0, 0), font=f_text)
    draw.text((400, 1290), "Signature of Claimant (Buyer)", fill=(0, 0, 0), font=f_text)
    draw.text((730, 1290), "Sub-Registrar Seal", fill=(0, 0, 0), font=f_label)

    return img


def generate_mutation_image(data=None) -> Image.Image:
    """Generate Mutation Register & Order (VF-6 / Dakhil-Kharij) document image."""
    data = data or DEFAULT_MUTATION_PAYLOAD
    img = Image.new("RGB", (1000, 1250), color=(250, 252, 250))
    draw = ImageDraw.Draw(img)

    f_title = _get_font(22, bold=True)
    f_sub = _get_font(16, bold=True)
    f_label = _get_font(13, bold=True)
    f_text = _get_font(13, bold=False)

    # Outer border
    draw.rectangle([20, 20, 980, 1230], outline=(30, 80, 40), width=3)

    # Header
    draw.text((500, 60), "OFFICE OF THE TEHSILDAR - REVENUE DIVISION", fill=(20, 60, 30), font=f_sub, anchor="mm")
    draw.text((500, 95), "MUTATION REGISTER & ORDER (DAKHIL-KHARIJ / VF-6)", fill=(10, 100, 40), font=f_title, anchor="mm")
    draw.line([50, 120, 950, 120], fill=(30, 80, 40), width=2)

    # Metadata Box
    mut_no = data.get("mutation_serial_number", "MUT-2024-0012")
    case_ref = data.get("case_reference_no", "REV/TEH/2024/782")
    nature = data.get("nature_of_mutation", "SUCCESSION_INHERITANCE")

    draw.rectangle([50, 140, 950, 230], fill=(235, 245, 235), outline=(80, 140, 80), width=2)
    draw.text((70, 160), f"MUTATION SERIAL NO: {mut_no}", fill=(0, 0, 0), font=f_sub)
    draw.text((500, 160), f"CASE REF NO: {case_ref}", fill=(0, 0, 0), font=f_sub)
    draw.text((70, 195), f"NATURE OF MUTATION: {nature}", fill=(20, 80, 140), font=f_sub)
    draw.text((600, 195), f"SANCTIONED DATE: {data.get('sanctioned_date', '2024-02-18')}", fill=(0, 120, 30), font=f_label)

    # Table of Transfer Details
    draw.text((50, 260), "MUTATION RECORD DETAILS", fill=(20, 60, 30), font=f_sub)
    draw.rectangle([50, 290, 950, 520], outline=(60, 60, 60), width=2)

    cols = [50, 220, 450, 680, 950]
    headers = ["Survey Affected", "Prior Owner (Transferor)", "New Owner (Transferee)", "Khata Transition"]
    draw.rectangle([50, 290, 950, 330], fill=(210, 230, 210))
    for i in range(len(headers)):
        draw.line([cols[i], 290, cols[i], 520], fill=(60, 60, 60), width=1)
        draw.text(((cols[i] + cols[i+1])//2, 310), headers[i], fill=(0, 0, 0), font=f_label, anchor="mm")
    draw.line([cols[-1], 290, cols[-1], 520], fill=(60, 60, 60), width=1)
    draw.line([50, 330, 950, 330], fill=(60, 60, 60), width=2)

    surveys = ", ".join(data.get("survey_numbers_affected", ["142/3B"]))
    transferor = data.get("transferor_prior_owner", {})
    transferee = data.get("transferee_new_owner", {})

    draw.text(((cols[0]+cols[1])//2, 380), surveys, fill=(0, 0, 0), font=f_text, anchor="mm")
    draw.text(((cols[1]+cols[2])//2, 380), f"{transferor.get('name', 'M. Murugan')}", fill=(0, 0, 0), font=f_text, anchor="mm")
    draw.text(((cols[2]+cols[3])//2, 380), f"{transferee.get('name', 'K. Raman')}", fill=(0, 0, 0), font=f_text, anchor="mm")
    draw.text(((cols[3]+cols[4])//2, 380), f"Khata {transferor.get('prior_khata_no', '310')} -> Khata {transferee.get('new_khata_no', '489')}", fill=(0, 0, 0), font=f_text, anchor="mm")

    # Application Dates
    draw.text((70, 460), f"Application Date: {data.get('applied_date', '2024-01-10')}", fill=(60, 60, 60), font=f_text)
    draw.text((500, 460), f"Share Acquired: {transferee.get('share_fraction', 1.0) * 100:.0f}%", fill=(60, 60, 60), font=f_text)

    # Sanctioning Authority Box
    auth = data.get("sanctioning_authority", {})
    draw.text((50, 560), "SANCTIONING AUTHORITY ORDER", fill=(20, 60, 30), font=f_sub)
    draw.rectangle([50, 590, 950, 750], fill=(255, 255, 255), outline=(80, 140, 80), width=1)
    draw.text((70, 620), f"Order: Mutation sanctioned in favor of {transferee.get('name', 'K. Raman')} for Survey {surveys}.", fill=(0, 0, 0), font=f_text)
    draw.text((70, 650), f"Officer: {auth.get('officer_designation', 'Tehsildar')}, Subdivision: {auth.get('subdivision', 'Sriperumbudur')}", fill=(0, 0, 0), font=f_text)
    draw.text((70, 680), f"Digital Signature Verified: {auth.get('digital_signature_verified', True)}", fill=(0, 120, 30), font=f_label)

    # Stamp
    draw.ellipse([700, 800, 880, 980], outline=(0, 100, 30), width=3)
    draw.text((790, 880), "SEAL OF TEHSILDAR\nSRIPERUMBUDUR", fill=(0, 100, 30), font=f_label, anchor="mm", align="center")

    return img


def generate_map_image(data=None) -> Image.Image:
    """Generate Spatial Cadastral Map (Bhu-Naksha / FMB) document image."""
    data = data or DEFAULT_MAP_PAYLOAD
    img = Image.new("RGB", (1100, 1300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    f_title = _get_font(22, bold=True)
    f_sub = _get_font(15, bold=True)
    f_label = _get_font(13, bold=True)
    f_text = _get_font(12, bold=False)

    # Outer border
    draw.rectangle([20, 20, 1080, 1280], outline=(0, 0, 0), width=3)

    # Header
    sheet = data.get("map_sheet_number", "Sheet-04")
    epsg = data.get("projection_system", "EPSG:4326")
    draw.text((550, 50), f"FIELD MEASUREMENT BOOK (FMB) / BHU-NAKSHA CADASTRAL MAP", fill=(0, 40, 100), font=f_title, anchor="mm")
    draw.text((550, 85), f"MAP SHEET: {sheet} | PROJECTION: {epsg}", fill=(80, 80, 80), font=f_sub, anchor="mm")
    draw.line([40, 110, 1060, 110], fill=(0, 0, 0), width=2)

    # Feature info
    feature = data.get("extracted_features", [{}])[0]
    khasra = feature.get("khasra_survey_number", "142/3B")
    gis_area = feature.get("calculated_gis_area_sqm", 1821.50)
    centroid = feature.get("centroid", {})

    draw.rectangle([40, 130, 1060, 190], fill=(240, 245, 255), outline=(100, 140, 200), width=1)
    draw.text((60, 150), f"TARGET SURVEY NO: {khasra}", fill=(0, 0, 0), font=f_sub)
    draw.text((380, 150), f"GIS CALCULATED AREA: {gis_area} sqm", fill=(0, 0, 0), font=f_sub)
    draw.text((750, 150), f"CENTROID: {centroid.get('latitude', 12.98112)} N, {centroid.get('longitude', 79.94155)} E", fill=(20, 80, 160), font=f_label)

    # Map Canvas Box
    draw.rectangle([50, 220, 1050, 950], fill=(250, 252, 255), outline=(0, 0, 0), width=2)

    # Compass North Arrow
    nx, ny = 980, 290
    draw.line([nx, ny, nx, ny - 50], fill=(0, 0, 0), width=3)
    draw.polygon([(nx, ny - 65), (nx - 10, ny - 45), (nx + 10, ny - 45)], fill=(0, 0, 0))
    draw.text((nx, ny - 75), "N", fill=(0, 0, 0), font=f_title, anchor="mm")

    # Plot Polygon Drawing (Target Khasra 142/3B)
    pts = [(300, 400), (800, 420), (760, 800), (260, 770)]
    draw.polygon(pts, fill=(230, 240, 255), outline=(0, 80, 200), width=4)

    # Draw Corner Vertices & Labels
    markers = ["G1", "G2", "G3", "G4"]
    for i, p in enumerate(pts):
        draw.ellipse([p[0]-6, p[1]-6, p[0]+6, p[1]+6], fill=(220, 20, 20), outline=(0,0,0), width=1)
        draw.text((p[0] + (15 if i in [1,2] else -25), p[1] + (15 if i in [2,3] else -25)), markers[i], fill=(200, 0, 0), font=f_label)

    # Tie Line Measurement (G1 to G2)
    tie = data.get("tie_line_measurements", [{}])[0]
    dist = tie.get("field_distance_meters", 45.2)
    draw.line([pts[0][0], pts[0][1]-15, pts[1][0], pts[1][1]-15], fill=(220, 20, 20), width=2)
    draw.text(((pts[0][0]+pts[1][0])//2, pts[0][1]-30), f"Tie Line {tie.get('from_marker','G1')}-{tie.get('to_marker','G2')}: {dist}m", fill=(200, 0, 0), font=f_label, anchor="mm")

    # Target Label inside polygon
    draw.text((530, 580), f"SURVEY NO: {khasra}", fill=(0, 40, 140), font=f_title, anchor="mm")
    draw.text((530, 620), f"Area: {gis_area} sqm", fill=(0, 40, 140), font=f_sub, anchor="mm")

    # Adjacent Survey Polygons
    # North: Survey 141
    draw.rectangle([200, 250, 900, 395], outline=(150, 150, 150), width=1)
    draw.text((530, 320), "Survey No 141 (Public Canal / North Boundary)", fill=(100, 100, 100), font=f_text, anchor="mm")

    # South: Village Road
    draw.rectangle([200, 805, 900, 920], outline=(150, 150, 150), width=1)
    draw.text((530, 860), "Village Panchayat Road (South Boundary)", fill=(100, 100, 100), font=f_text, anchor="mm")

    # East: 142/3A
    draw.text((880, 600), "Survey 142/3A\n(East)", fill=(100, 100, 100), font=f_text, anchor="mm")

    # West: 143
    draw.text((150, 600), "Survey 143\n(West)", fill=(100, 100, 100), font=f_text, anchor="mm")

    # Table 5: Map Legend & Attributes
    draw.text((50, 980), "CADASTRAL MAP LEGEND & ATTRIBUTES", fill=(0, 40, 100), font=f_sub)
    draw.rectangle([50, 1010, 1050, 1220], fill=(250, 250, 250), outline=(60, 60, 60), width=1)
    draw.text((70, 1030), f"• Map Sheet: {sheet}", fill=(0, 0, 0), font=f_text)
    draw.text((70, 1060), f"• Target Survey/Khasra: {khasra}", fill=(0, 0, 0), font=f_text)
    draw.text((70, 1090), f"• Geometry Type: {feature.get('geometry_type', 'Polygon')}", fill=(0, 0, 0), font=f_text)
    draw.text((70, 1120), f"• Coordinates: {feature.get('coordinates', [])}", fill=(0, 0, 0), font=f_text)
    draw.text((70, 1150), f"• Calculated Area: {gis_area} sqm", fill=(0, 0, 0), font=f_text)
    draw.text((70, 1180), f"• Centroid Lat/Long: {centroid.get('latitude', 12.98112)}, {centroid.get('longitude', 79.94155)}", fill=(0, 0, 0), font=f_text)

    return img


def generate_document_image(doc_type: str, data=None) -> Image.Image:
    """Factory function to generate document image by type string."""
    doc_type_upper = doc_type.upper()
    if "ROR" in doc_type_upper or "PATTA" in doc_type_upper or "RIGHTS" in doc_type_upper:
        return generate_ror_image(data)
    elif "DEED" in doc_type_upper or "SALE" in doc_type_upper or "CONVEYANCE" in doc_type_upper:
        return generate_deed_image(data)
    elif "MUTATION" in doc_type_upper or "VF-6" in doc_type_upper or "KHARIJ" in doc_type_upper:
        return generate_mutation_image(data)
    elif "MAP" in doc_type_upper or "CADASTRAL" in doc_type_upper or "FMB" in doc_type_upper:
        return generate_map_image(data)
    else:
        return generate_ror_image(data)
