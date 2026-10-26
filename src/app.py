import streamlit as st
import pandas as pd
from src.schemas import DeployEvaluationRequest, PatientInferencePayload
from src.validator import CICDDeployValidator

st.set_page_config(
    page_title="Automated Model CI/CD & Deploy Gatekeeper",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Enterprise MLOps CI/CD & Model Deploy Gatekeeper")
st.markdown("""
Pipeline contínuo de **validação de contratos**, **prevenção de regressão estatística** e **aprovação automatizada de releases** para modelos clínicos em ambiente hospitalar.
""")

tab1, tab2, tab3 = st.tabs(["🚦 Avaliação de Release Candidate", "⚡ Teste de Inferência em Tempo Real", "📝 Relatório CML para Pull Requests"])

with tab1:
    st.subheader("Configurar Parâmetros da Release Candidate")
    col1, col2 = st.columns(2)
    with col1:
        cand_v = st.text_input("Versão Candidata", "v2.2.0-rc1")
        ref_v = st.text_input("Versão de Produção Atual", "v2.1.0-prod")
        cand_auc = st.slider("ROC-AUC do Modelo Candidato", 0.50, 1.00, 0.915, 0.005)
        ref_auc = st.slider("ROC-AUC do Modelo em Produção", 0.50, 1.00, 0.902, 0.005)

    with col2:
        cand_recall = st.slider("Recall Clínico (Sensibilidade)", 0.50, 1.00, 0.84, 0.01)
        min_recall = st.slider("Quality Gate Mínimo de Recall", 0.70, 0.95, 0.80, 0.01)
        latency_p95 = st.slider("Latência P95 Registrada (ms)", 5.0, 100.0, 24.5, 0.5)
        max_lat = st.slider("SLO Máximo de Latência Permitido (ms)", 10.0, 100.0, 50.0, 5.0)

    req = DeployEvaluationRequest(
        candidate_model_version=cand_v,
        reference_model_version=ref_v,
        candidate_roc_auc=cand_auc,
        reference_roc_auc=ref_auc,
        candidate_recall=cand_recall,
        min_recall_threshold=min_recall,
        candidate_p95_latency_ms=latency_p95,
        max_allowed_latency_ms=max_lat
    )
    report = CICDDeployValidator.evaluate_release_candidate(req)

    st.markdown("### Decisão do Quality Gate")
    if report.deployment_allowed:
        st.success(f"✅ **RELEASE APROVADA**: {report.decision_reason}")
    else:
        st.error(f"🛑 **DEPLOY BLOQUEADO**: {report.decision_reason}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Checagem de AUC", "APROVADO" if report.checks["auc_regression_check"] else "REPROVADO")
    c2.metric("Checagem de Sensibilidade", "APROVADO" if report.checks["clinical_recall_threshold"] else "REPROVADO")
    c3.metric("Checagem de Latência SLO", "APROVADO" if report.checks["p95_latency_slo"] else "REPROVADO")

with tab2:
    st.subheader("Validação de Contrato de Dados (Simulação de Inferência REST)")
    col_a, col_b = st.columns(2)
    with col_a:
        p_id = st.text_input("ID do Paciente", "PAC-94821")
        age = st.number_input("Idade", 18, 100, 68)
        bp = st.number_input("Pressão Sistólica (mmHg)", 60, 220, 142)
    with col_b:
        hr = st.number_input("Frequência Cardíaca (bpm)", 40, 180, 88)
        creat = st.number_input("Creatinina (mg/dL)", 0.2, 10.0, 1.8)
        o2 = st.number_input("Saturação de O2 (%)", 70, 100, 93)

    payload = PatientInferencePayload(
        patient_id=p_id,
        age=age,
        systolic_bp=bp,
        heart_rate=hr,
        creatinine_mg_dl=creat,
        oxygen_sat_pct=o2
    )

    if st.button("Executar Inferência e Validar Contrato"):
        res = CICDDeployValidator.simulate_mock_inference(payload, cand_v)
        st.success("Contrato Pydantic validado com sucesso!")
        st.json(res.model_dump())

with tab3:
    st.subheader("Visualização do Comentário CML Injetado no GitHub Actions")
    st.markdown(report.cml_markdown_summary)
