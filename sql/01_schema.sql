-- Esquema estrela do projeto. Rodar no PostgreSQL da Aiven.
-- psql "$PG_URI" -f sql/01_schema.sql

CREATE TABLE IF NOT EXISTS dim_municipio (
    cod_ibge            CHAR(7) PRIMARY KEY,
    nome                TEXT NOT NULL,
    uf                  CHAR(2) NOT NULL,
    pct_preta_parda     NUMERIC(5,2),          -- Censo 2022
    faixa_racial        TEXT                   -- 'até 30%', '30% a 50%', '50% a 70%', 'acima de 70%'
);

CREATE TABLE IF NOT EXISTS dim_orgao (
    cnpj_orgao          CHAR(14) PRIMARY KEY,
    razao_social        TEXT NOT NULL,
    esfera              TEXT,                  -- federal / estadual / municipal
    uf                  CHAR(2),
    cod_ibge            CHAR(7) REFERENCES dim_municipio(cod_ibge)
);

CREATE TABLE IF NOT EXISTS dim_fornecedor (
    cnpj                    CHAR(14) PRIMARY KEY,
    razao_social            TEXT,
    porte                   TEXT,              -- MEI / ME / EPP / Demais
    cnae_principal          CHAR(7),
    uf                      CHAR(2),
    cod_ibge                CHAR(7) REFERENCES dim_municipio(cod_ibge),
    qtd_socios              SMALLINT,
    qtd_socias              SMALLINT,
    qtd_indeterminados      SMALLINT,
    tem_socia               BOOLEAN NOT NULL DEFAULT FALSE,
    maioria_feminina        BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS dim_socio (
    id                      BIGSERIAL PRIMARY KEY,
    cnpj                    CHAR(14) REFERENCES dim_fornecedor(cnpj),
    primeiro_nome           TEXT,              -- só o primeiro nome é guardado
    qualificacao            TEXT,
    genero_inferido         TEXT CHECK (genero_inferido IN ('F','M','indeterminado')),
    confianca_inferencia    NUMERIC(4,3)
);

CREATE TABLE IF NOT EXISTS fato_contrato (
    id_contrato_pncp        TEXT PRIMARY KEY,  -- numeroControlePNCP
    cnpj_fornecedor         CHAR(14) REFERENCES dim_fornecedor(cnpj),
    cnpj_orgao              CHAR(14) REFERENCES dim_orgao(cnpj_orgao),
    data_assinatura         DATE NOT NULL,
    valor_global            NUMERIC(16,2) NOT NULL CHECK (valor_global >= 0),
    modalidade              TEXT,
    tipo_contrato           TEXT,
    objeto                  TEXT
);

CREATE INDEX IF NOT EXISTS ix_fato_data       ON fato_contrato (data_assinatura);
CREATE INDEX IF NOT EXISTS ix_fato_fornecedor ON fato_contrato (cnpj_fornecedor);
CREATE INDEX IF NOT EXISTS ix_fato_orgao      ON fato_contrato (cnpj_orgao);

-- Visão agregada que o dashboard consome (contrato de dados com o app).
-- Mesmas colunas de app/sample/painel.csv.
DROP MATERIALIZED VIEW IF EXISTS mv_painel;
CREATE MATERIALIZED VIEW mv_painel AS
SELECT
    m.uf,
    m.nome                                  AS municipio,
    m.faixa_racial,
    EXTRACT(YEAR  FROM c.data_assinatura)::INT AS ano,
    EXTRACT(MONTH FROM c.data_assinatura)::INT AS mes,
    o.razao_social                          AS orgao,
    COALESCE(c.modalidade, 'Não informada') AS modalidade,
    COALESCE(f.porte, 'Não informado')      AS porte,
    COUNT(*)                                AS qtd_contratos,
    COUNT(DISTINCT c.cnpj_fornecedor)       AS qtd_fornecedores,
    SUM(c.valor_global)                     AS valor_total,
    SUM(c.valor_global) FILTER (WHERE f.tem_socia)        AS valor_com_socia,
    SUM(c.valor_global) FILTER (WHERE f.maioria_feminina) AS valor_maioria_feminina
FROM fato_contrato c
JOIN dim_fornecedor f ON f.cnpj = c.cnpj_fornecedor
JOIN dim_municipio  m ON m.cod_ibge = f.cod_ibge
LEFT JOIN dim_orgao o ON o.cnpj_orgao = c.cnpj_orgao
GROUP BY 1,2,3,4,5,6,7,8;

-- Indicador de qualidade da inferência de gênero
CREATE OR REPLACE VIEW vw_qualidade_genero AS
SELECT
    COUNT(*)                                                         AS total_socios,
    COUNT(*) FILTER (WHERE genero_inferido = 'indeterminado')        AS indeterminados,
    ROUND(100.0 * COUNT(*) FILTER (WHERE genero_inferido <> 'indeterminado') / NULLIF(COUNT(*),0), 1)
                                                                     AS pct_inferido
FROM dim_socio;

-- Atualizar após cada carga:
-- REFRESH MATERIALIZED VIEW mv_painel;
