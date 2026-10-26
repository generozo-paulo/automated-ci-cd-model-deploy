import time
from typing import Dict, Any
from src.schemas import DeployEvaluationRequest, DeployEvaluationReport, PatientInferencePayload, InferenceResponse

class CICDDeployValidator:
    """
    Motor avaliador de qualidade e segurança para esteiras automatizadas de CI/CD de Modelos.
    """

    @staticmethod
    def evaluate_release_candidate(request: DeployEvaluationRequest) -> DeployEvaluationReport:
        checks: Dict[str, bool] = {}

        # 1. Checagem de degradação de ROC-AUC
        auc_delta = request.candidate_roc_auc - request.reference_roc_auc
        checks["auc_regression_check"] = bool(auc_delta >= -request.max_allowed_auc_drop)

        # 2. Checagem de sensibilidade clínica mínima
        checks["clinical_recall_threshold"] = bool(request.candidate_recall >= request.min_recall_threshold)

        # 3. Checagem de SLO de latência P95
        checks["p95_latency_slo"] = bool(request.candidate_p95_latency_ms <= request.max_allowed_latency_ms)

        all_passed = all(checks.values())
        status = "PASSED" if all_passed else "FAILED"

        reasons = []
        if not checks["auc_regression_check"]:
            reasons.append(f"Regressão inaceitável de AUC (Delta: {auc_delta:.4f} < -{request.max_allowed_auc_drop})")
        if not checks["clinical_recall_threshold"]:
            reasons.append(f"Sensibilidade insuficiente ({request.candidate_recall:.2%} < {request.min_recall_threshold:.2%})")
        if not checks["p95_latency_slo"]:
            reasons.append(f"Latência P95 acima do SLO ({request.candidate_p95_latency_ms:.1f}ms > {request.max_allowed_latency_ms:.1f}ms)")

        decision = "Aprovado para deploy em Produção" if all_passed else "; ".join(reasons)

        cml_markdown = f"""## 📊 CML Model Evaluation Report

| Validação | Candidato (`{request.candidate_model_version}`) | Referência (`{request.reference_model_version}`) | Tolerância | Status |
| :--- | :--- | :--- | :--- | :--- |
| **ROC-AUC** | `{request.candidate_roc_auc:.4f}` | `{request.reference_roc_auc:.4f}` | Max Drop: `{request.max_allowed_auc_drop}` | {'✅ PASS' if checks['auc_regression_check'] else '❌ FAIL'} |
| **Recall Clínico** | `{request.candidate_recall:.2%}` | - | Min: `{request.min_recall_threshold:.2%}` | {'✅ PASS' if checks['clinical_recall_threshold'] else '❌ FAIL'} |
| **Latência P95** | `{request.candidate_p95_latency_ms:.1f}ms` | - | Max SLO: `{request.max_allowed_latency_ms:.1f}ms` | {'✅ PASS' if checks['p95_latency_slo'] else '❌ FAIL'} |

**Decisão do Gatekeeper**: `{'🚀 APPROVED FOR DEPLOY' if all_passed else '🛑 BLOCKED BY QUALITY GATE'}`
"""
        return DeployEvaluationReport(
            status=status,
            checks=checks,
            cml_markdown_summary=cml_markdown,
            deployment_allowed=all_passed,
            decision_reason=decision
        )

    @staticmethod
    def simulate_mock_inference(payload: PatientInferencePayload, model_version: str = "v2.1.0-prod") -> InferenceResponse:
        t0 = time.perf_counter()
        # Modelo heurístico calibrado para testes de integração
        score = (
            (payload.age / 100.0) * 0.25 +
            (payload.creatinine_mg_dl / 3.0) * 0.35 +
            (1.0 - (payload.oxygen_sat_pct / 100.0)) * 0.40
        )
        prob = min(max(float(score), 0.01), 0.99)

        if prob >= 0.70:
            tier = "CRITICAL"
        elif prob >= 0.45:
            tier = "HIGH"
        elif prob >= 0.25:
            tier = "MODERATE"
        else:
            tier = "LOW"

        latency = (time.perf_counter() - t0) * 1000.0

        return InferenceResponse(
            patient_id=payload.patient_id,
            mortality_risk_probability=round(prob, 4),
            risk_tier=tier,
            model_version=model_version,
            latency_ms=round(latency, 2)
        )
