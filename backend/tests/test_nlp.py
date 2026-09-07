import pytest
from app.services.nlp.entity_extractor import EntityExtractor

def test_entity_extraction_and_mapping():
    ocr_text = """
    REVENUE DEPARTMENT - RECORD OF RIGHTS
    State: Maharashtra
    District: Pune
    Tehsil: Haveli
    Village: Wagholi
    Owner Name: Ramesh Kumar
    Father Name: Shyam Lal
    Survey Number: 123/4A
    Khata Number: 78/B
    Area: 2.3500 hectares
    Mutation Date: 12/03/2024
    """

    layout_pairs = {
        "state": "Maharashtra",
        "district": "Pune",
        "tehsil": "Haveli",
        "village": "Wagholi",
        "owner_name": "Ramesh Kumar",
        "survey_number": "123/4A",
        "area": "2.3500",
        "area_unit": "hectares"
    }

    entities = EntityExtractor.extract_entities(ocr_text, layout_pairs, [])

    assert entities["survey_number"][0] == "123/4A"
    assert entities["owner_name"][0] == "Ramesh Kumar"
    assert entities["village"][0] == "Wagholi"
    assert entities["area"][0] == 2.35
    assert entities["area_unit"][0] == "hectares"
