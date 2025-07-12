output "cloudsql_instance_connection_name" {
  value = google_sql_database_instance.langflow.connection_name
}

output "cloudsql_private_ip" {
  value = google_sql_database_instance.langflow.private_ip_address
}

output "redis_host" {
  value = google_redis_instance.langflow.host
}

output "ingress_ip" {
  value = google_compute_address.ingress_ip.address
} 