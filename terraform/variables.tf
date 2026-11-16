variable "aiven_api_token" {
  description = "Token da API da Aiven. Passe por TF_VAR_aiven_api_token."
  type        = string
  sensitive   = true
}

variable "aiven_project" {
  description = "Nome do projeto Aiven criado no console."
  type        = string
}

variable "pg_service_name" {
  description = "Nome do serviço PostgreSQL."
  type        = string
  default     = "pg-ods-compras"
}

variable "pg_plan" {
  description = "Plano do PostgreSQL. Confirme o nome do plano gratuito no console/Terraform Registry."
  type        = string
  default     = "free-1-1gb"
}

variable "cloud_name" {
  description = "Nuvem/região. Planos gratuitos só aceitam algumas; confira no console."
  type        = string
  default     = "do-nyc"
}
