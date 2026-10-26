# Especificação Contratual (SDD) - Automated CI/CD Model Deploy Pipeline

## 1. Escopo & Objetivos
Pipeline de integração e entrega contínua (CI/CD) para modelos preditivos em saúde.
Executa:
1. Validação de contratos de dados de entrada/saída (Model Contract Testing via Pydantic).
2. Avaliação de degradação de desempenho contra modelo de referência (Regression Quality Gate).
3. Teste de carga de latência de inferência (SLO < 50ms por requisição).
4. Emissão automática de relatório em Markdown com métricas para Pull Requests (CML - Continuous Machine Learning).
5. Build de imagem de container de inferência com FastAPI.

## 2. Contratos de Entrada (Pydantic)

### 2.1 Schema de Avaliação de Release (`DeployEvaluationRequest`)
- `candidate_model_version`: str
- `reference_model_version`: str
- `candidate_roc_auc`: float
- `reference_roc_auc`: float
- `max_allowed_auc_drop`: float = 0.015
- `min_recall_threshold`: float = 0.80
- `candidate_p95_latency_ms`: float
- `max_allowed_latency_ms`: float = 50.0

## 3. Contratos de Saída (Pydantic)

### 3.1 Relatório de Validação de CI/CD (`DeployEvaluationReport`)
- `status`: Literal["PASSED", "FAILED"]
- `checks`: Dict[str, bool]
- `cml_markdown_summary`: str
- `deployment_allowed`: bool
- `decision_reason`: str
