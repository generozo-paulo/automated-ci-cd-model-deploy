import pytest
from src.schemas import DeployEvaluationRequest, PatientInferencePayload
from src.validator import CICDDeployValidator

def test_deploy_evaluation_passing():
    req = DeployEvaluationRequest(
        candidate_model_version="v2.0.0",
        reference_model_version="v1.9.0",
        candidate_roc_auc=0.92,
        reference_roc_auc=0.90,
        candidate_recall=0.85,
        min_recall_threshold=0.80,
        candidate_p95_latency_ms=22.0,
        max_allowed_latency_ms=50.0
    )
    report = CICDDeployValidator.evaluate_release_candidate(req)
    assert report.deployment_allowed is True
    assert report.status == "PASSED"
    assert report.checks["auc_regression_check"] is True
    assert report.checks["clinical_recall_threshold"] is True
    assert report.checks["p95_latency_slo"] is True

def test_deploy_evaluation_blocked_by_recall():
    req = DeployEvaluationRequest(
        candidate_model_version="v2.0.1",
        reference_model_version="v2.0.0",
        candidate_roc_auc=0.94, # excelente AUC mas sensibilidade baixa
        reference_roc_auc=0.92,
        candidate_recall=0.72, # abaixo do limiar clínico de 80%
        min_recall_threshold=0.80,
        candidate_p95_latency_ms=20.0,
        max_allowed_latency_ms=50.0
    )
    report = CICDDeployValidator.evaluate_release_candidate(req)
    assert report.deployment_allowed is False
    assert report.status == "FAILED"
    assert report.checks["clinical_recall_threshold"] is False

def test_patient_contract_inference():
    payload = PatientInferencePayload(
        patient_id="PAC-TEST",
        age=55,
        systolic_bp=130.0,
        heart_rate=75.0,
        creatinine_mg_dl=1.1,
        oxygen_sat_pct=98.0
    )
    res = CICDDeployValidator.simulate_mock_inference(payload, "v2.0.0")
    assert res.patient_id == "PAC-TEST"
    assert 0.0 <= res.mortality_risk_probability <= 1.0
    assert res.risk_tier in ["LOW", "MODERATE", "HIGH", "CRITICAL"]
    assert res.latency_ms >= 0.0
