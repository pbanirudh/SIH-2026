import json

with open("tmp_rec3.json") as f:
    data = json.load(f)

print(f"Total records: {len(data)}")
for rec in data[:5]:
    non_null = [f for f in rec.get('fields', []) if f.get('field_value') is not None]
    print(f"\nID: {rec['id'][:12]}... | Type: {rec.get('document_type')} | Owner: {rec.get('owner_name')} | Survey: {rec.get('survey_number')}")
    print(f"  Non-null fields: {len(non_null)} / {len(rec.get('fields', []))}")
    for f in non_null:
        print(f"    {f['field_name']}: {f['field_value']}")
