"""Run the formal 3-loop input -> graph -> canonical-family audit."""
from three_loop.input_pipeline import write_input_to_family_audit


def main() -> None:
    json_path, md_path, audit = write_input_to_family_audit()
    print("QEDCalc 3-loop formal input pipeline")
    print(f"formal inputs: {audit['diagram_count']}")
    print(f"graph/registry: {audit['graph_registry_exact_match_count']}/72")
    print(f"canonical families: {audit['canonical_family_count']}")
    print(f"classification complete: {audit['classification_complete']}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    if not audit["audit_pass"]:
        for item in audit["errors"]:
            print("ERROR:", item)
        raise SystemExit(1)
    print("QEDCalc 3-loop input -> canonical-family audit PASS")


if __name__ == "__main__":
    main()
