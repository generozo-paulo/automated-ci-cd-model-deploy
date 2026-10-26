from pydantic import BaseModel, Field
from typing import Dict, Literal

class PatientInferencePayload(BaseModel):
    patient_id: str
    age: int = Field(ge=0, le=125)
    systolic_bp: float = Field(ge=40.0, le=260.0)
    heart_rate: float = Field(ge=20.0, le=240.0)
    creatinine_mg_dl: float = Field(ge=0.1, le=25.0)
    oxygen_sat_pct: float = Field(ge=50.0, le=100.0)

class InferenceResponse(BaseModel):
    patient_id: str
    mortality_risk_probability: float
    risk_tier: Literal["LOW", "MODERATE", "HIGH", "CRITICAL"]
    model_version: str
    latency_ms: float

class DeployEvaluationRequest(BaseModel):
    candidate_model_version: str
    reference_model_version: str
    candidate_roc_auc: float = Field(ge=0.0, le=1.0)
    reference_roc_auc: float = Field(ge=0.0, le=1.0)
    candidate_recall: float = Field(ge=0.0, le=1.0)
    min_recall_threshold: float = Field(default=0.80, ge=0.0, le=1.0)
    max_allowed_auc_drop: float = Field(default=0.015, ge=0.0)
    candidate_p95_latency_ms: float = Field(gt=0.0)
    max_allowed_latency_ms: float = Field(default=50.0, gt=0.0)

class DeployEvaluationReport(BaseModel):
    status: Literal["PASSED", "FAILED"]
    checks: Dict[str, bool]
    cml_markdown_summary: str
    deployment_allowed: bool
    decision_reason: str
