import json
from pathlib import Path
from jsonschema import Draft202012Validator

SCHEMA = Path(__file__).parents[1] / "references" / "notice-sidecar-schema.json"


def test_schema_is_itself_valid_draft2020():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)  # raises if the schema is malformed


def test_notice_type_enum_has_the_five_skill_types_plus_combined():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["properties"]["notice"]["properties"]["notice_type"]["enum"] == [
        "website_app", "applicant", "employee", "business_partner", "b2c_customer", "combined"]


def test_contested_items_require_the_confirm_with_counsel_flag_field():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    contested = schema["properties"]["confidence"]["properties"]["contested"]["items"]
    assert "confirm_with_counsel_flag_emitted" in contested["required"]
