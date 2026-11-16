# Compras Públicas, Gênero e Raça (ODS 5 e ODS 18)

Pipeline de dados em nuvem, a custo zero, que mede quanto das compras públicas vai para empresas com sócias mulheres e como isso varia entre territórios com diferentes composições raciais.

**Equipe:** Caio Vitorino, Fabio Telles, Luiz Salles, Thalisson Gabriel, Mateus Bastos
**Disciplina:** Computação em Nuvem / Engenharia de Software

## Pergunta analítica

> Qual a participação de empresas com sócias mulheres nas compras públicas e como ela varia entre territórios com diferentes composições raciais?

## Arquitetura

```mermaid
flowchart LR
    PNCP[PNCP<br/>contratos via API] --> ETL
    RF[Receita Federal<br/>CNPJ: empresas e sócios] --> ETL
    IBGE[IBGE<br/>nomes e Censo 2022] --> ETL
    ETL[ETL em Python<br/>DuckDB e Parquet] -->|carga| PG
    subgraph Aiven [Aiven - plano gratuito]
        PG[(PostgreSQL 1 GB<br/>modelo estrela)]
        K[Kafka - opcional]
        OS[OpenSearch - opcional]
    end
    TF[Terraform] -. provisiona .-> Aiven
    PG --> ST[Streamlit Community Cloud<br/>dashboard]
```

O processamento pesado acontece fora do banco (Parquet/DuckDB). O PostgreSQL recebe só os dados filtrados do recorte, para caber em 1 GB.

## Estrutura do repositório

| Pasta | Conteúdo |
| --- | --- |
| `terraform/` | Provisionamento dos serviços Aiven |
| `etl/` | Extração do PNCP, inferência de gênero e carga no PostgreSQL |
| `sql/` | Esquema estrela, view do painel e testes de qualidade |
| `app/` | Dashboard Streamlit |
| `.github/workflows/` | Keep-alive do banco |
| `docs/` | Diagramas e material de apoio |

## Como executar

### 1. Pré-requisitos
- Python 3.11+, Terraform 1.5+, `psql`
- Conta na Aiven com um projeto criado e um token de API

### 2. Infraestrutura
```bash
cp .env.example .env                       # preencha o token
export $(grep -v '^#' .env | xargs)
cd terraform
cp terraform.tfvars.example terraform.tfvars   # preencha o nome do projeto
terraform init
terraform apply
terraform output
```

### 3. Banco de dados
```bash
psql "postgres://avnadmin:SENHA@HOST:PORTA/defaultdb?sslmode=require" -f sql/01_schema.sql
```

### 4. ETL
```bash
pip install -r etl/requirements.txt
python etl/extract_pncp.py --inicio 20240101 --fim 20240131
# tratamento CNPJ + gênero + Censo -> data/processed/*.parquet
python etl/load_postgres.py
psql "..." -f sql/02_testes_qualidade.sql
```

### 5. Dashboard
```bash
pip install -r app/requirements.txt
python app/gerar_amostra.py        # só para desenvolver sem o banco
streamlit run app/app.py
```
Sem `app/.streamlit/secrets.toml`, o app usa dados sintéticos e mostra um aviso. Com o arquivo (modelo em `secrets.toml.example`), lê a view `mv_painel` da Aiven.

Para publicar: [share.streamlit.io](https://share.streamlit.io) → New app → arquivo `app/app.py` → cole os secrets em *Settings › Secrets*.

## Dicionário de variáveis

### Fontes públicas
| Campo | Fonte | Descrição |
| --- | --- | --- |
| `numeroControlePNCP` | PNCP | Identificador único do contrato |
| `niFornecedor` | PNCP | CNPJ do fornecedor |
| `valorGlobal` | PNCP | Valor global do contrato (R$) |
| `dataAssinatura` | PNCP | Data de assinatura |
| `orgaoEntidade.cnpj` | PNCP | CNPJ do órgão contratante |
| `nome_socio` | CNPJ (Receita) | Nome do sócio no quadro societário |
| `qualificacao_socio` | CNPJ (Receita) | Papel do sócio na empresa |
| `porte_empresa` | CNPJ (Receita) | Porte declarado |
| `cnae_fiscal_principal` | CNPJ (Receita) | Atividade econômica |
| `pct_preta_parda` | Censo 2022 (IBGE) | % de população preta e parda do município |

### Campos derivados
| Campo | Regra |
| --- | --- |
| `genero_inferido` | F, M ou indeterminado, pelo primeiro nome (limiar de 90%) |
| `confianca_inferencia` | Proporção do sexo predominante para aquele nome |
| `tem_socia` | Empresa tem ao menos uma sócia |
| `maioria_feminina` | Mais da metade dos sócios classificados é mulher |
| `faixa_racial` | até 30%, 30% a 50%, 50% a 70%, acima de 70% |

> Confira os nomes exatos dos campos do PNCP no [Swagger da API](https://pncp.gov.br/api/consulta/swagger-ui/index.html).

## Limitações

- **Raça e gênero não existem nas bases públicas.** O quadro societário traz nome e qualificação, com CPF mascarado.
- **Gênero é inferido** pelo primeiro nome com a base de nomes do IBGE. Nomes ambíguos ficam como indeterminados e o percentual é exibido no painel. A taxa de acerto foi validada em uma amostra revisada manualmente (preencher).
- **Raça é contexto territorial**, não atributo da empresa: o painel mostra a participação feminina por faixa de população preta e parda do município.
- Só agregados são exibidos. Nenhuma empresa ou pessoa é rotulada individualmente.

## Segurança

Tokens e senhas ficam em `.env`, `terraform.tfvars`, `secrets.toml` ou GitHub Secrets, todos fora do Git. Antes de cada entrega: `git log -p | grep -i -E "token|password"`.
