# CRISP-DM: Implementação e Deploy de Modelos (Deployment Phase)

## 1. Problema de Engenharia MLOps
Modelos de Machine Learning treinados localmente frequentemente falham em produção devido a:
- Mudança na ordem ou tipos de colunas esperadas.
- Aumento imprevisto de latência em cenários de alta concorrência hospitalar.
- Regressão silenciosa de sensibilidade clínica em subgrupos vulneráveis.

## 2. Abordagem de CI/CD para Modelos Clínicos
O deploy contínuo em saúde exige um pipeline automatizado com barreiras (**gates**) intransponíveis:
1. **Linter e Contract Tests**: Validação rigorosa do payload JSON contra schemas Pydantic.
2. **Quality Gate Comparativo**: O modelo candidato não pode apresentar queda estatística em relação ao modelo em produção.
3. **Latência Máxima Aceitável**: P95 inferior a 50 milissegundos para prontuário eletrônico.
4. **Relatório CML Automático**: Injeção do relatório de métricas como comentário no GitHub PR.
