from src.services.check_service import validate_submission


def test_required_fields_and_attachments_are_errors():
    errors, warnings = validate_submission(
        {"construction_code": "A-001", "attachments": ["申請書"]},
        {
            "required_fields": ["construction_code", "target_year_month"],
            "required_attachments": ["申請書", "見積書"],
        },
    )

    assert {error["field"] for error in errors} == {"target_year_month", "attachments"}
    assert warnings == []


def test_construction_master_mismatch_is_warning():
    errors, warnings = validate_submission(
        {
            "construction_code": "A-001",
            "construction_name": "別名",
            "branch_code": "BR-01",
            "site_code": "SITE-01",
        },
        {
            "construction_master": {
                "A-001": {
                    "construction_name": "正しい工事名",
                    "branch_code": "BR-01",
                    "site_code": "SITE-01",
                }
            }
        },
    )

    assert errors == []
    assert warnings == [
        {
            "field": "construction_name",
            "message": "工事コードと工事マスタの情報が一致していません",
        }
    ]
