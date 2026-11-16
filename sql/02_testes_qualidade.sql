-- Testes de qualidade dos dados. Cada consulta deve retornar 0.

-- Contratos duplicados
SELECT COUNT(*) - COUNT(DISTINCT id_contrato_pncp) AS duplicados FROM fato_contrato;

-- Valores negativos ou nulos
SELECT COUNT(*) AS valores_invalidos FROM fato_contrato WHERE valor_global IS NULL OR valor_global < 0;

-- Datas fora do recorte (ajuste o intervalo)
SELECT COUNT(*) AS datas_fora FROM fato_contrato
WHERE data_assinatura NOT BETWEEN DATE '2023-01-01' AND DATE '2024-12-31';

-- Contratos sem fornecedor cadastrado
SELECT COUNT(*) AS sem_fornecedor FROM fato_contrato c
LEFT JOIN dim_fornecedor f ON f.cnpj = c.cnpj_fornecedor WHERE f.cnpj IS NULL;

-- Tamanho do banco (precisa ficar abaixo de ~700 MB)
SELECT pg_size_pretty(pg_database_size(current_database())) AS tamanho_banco;
