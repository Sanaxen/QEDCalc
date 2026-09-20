from three_loop.input_pipeline import build_input_to_family_audit, load_three_loop_inputs


def test_three_loop_formal_input_inventory():
    rows = load_three_loop_inputs()
    assert len(rows) == 72
    assert rows[0].diagram_id == "Q01"
    assert rows[-1].diagram_id == "LBL06"


def test_three_loop_inputs_connect_to_existing_canonical_families():
    audit = build_input_to_family_audit()
    assert audit["diagram_count"] == 72
    assert audit["graph_registry_exact_match_count"] == 72
    assert audit["graph_registry_pass"]
    assert audit["canonical_classification_pass"]
    assert audit["classification_complete"]
    assert audit["canonical_family_count"] == 45
    assert audit["audit_pass"]
