# Só host e porta. A senha NÃO é exposta como output.
output "pg_host" {
  value = aiven_pg.principal.service_host
}

output "pg_port" {
  value = aiven_pg.principal.service_port
}

output "pg_service_uri_sem_senha" {
  value = "postgres://avnadmin@${aiven_pg.principal.service_host}:${aiven_pg.principal.service_port}/defaultdb?sslmode=require"
}
