terraform {
  required_version = ">= 1.5"
  required_providers {
    aiven = {
      source  = "aiven/aiven"
      version = ">= 4.0.0"
    }
  }
}

# O token vem de TF_VAR_aiven_api_token (variável de ambiente), nunca do código.
provider "aiven" {
  api_token = var.aiven_api_token
}

# Projeto criado no console da Aiven por um integrante.
data "aiven_project" "projeto" {
  project = var.aiven_project
}

# Banco principal: PostgreSQL no plano gratuito (1 CPU, 1 GB RAM, 1 GB disco).
resource "aiven_pg" "principal" {
  project      = data.aiven_project.projeto.project
  service_name = var.pg_service_name
  plan         = var.pg_plan
  cloud_name   = var.cloud_name

  pg_user_config {
    pg_version = "16"
  }
}

# --- Opcional: Kafka e OpenSearch no plano gratuito ---
# Descomente só depois que o núcleo (PostgreSQL + dashboard) estiver estável.
# Confirme o nome dos planos gratuitos no console antes de aplicar.
#
# resource "aiven_kafka" "streaming" {
#   project      = data.aiven_project.projeto.project
#   service_name = "kafka-ods"
#   plan         = "free-0"
#   cloud_name   = var.cloud_name
# }
#
# resource "aiven_opensearch" "busca" {
#   project      = data.aiven_project.projeto.project
#   service_name = "opensearch-ods"
#   plan         = "free-1"
#   cloud_name   = var.cloud_name
# }
