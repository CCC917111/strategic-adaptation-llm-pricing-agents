import json

from pricing_experiment.persistence import ExperimentStore


def test_completed_manifest_drops_stale_failure_fields(tmp_path) -> None:
    manifest = {
        "status": "failed",
        "error": "temporary network failure",
        "error_type": "ConnectError",
        "failed_at": "earlier",
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))

    ExperimentStore(tmp_path).finish(stopping={"reason": "converged"})

    completed = json.loads((tmp_path / "manifest.json").read_text())
    assert completed["status"] == "completed"
    assert completed["stopping"] == {"reason": "converged"}
    assert "error" not in completed
    assert "error_type" not in completed
    assert "failed_at" not in completed
