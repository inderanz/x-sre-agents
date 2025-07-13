# Outputs for the x-sre-agents GKE infrastructure

output "cluster_name" {
  description = "The name of the GKE cluster"
  value       = google_container_cluster.primary.name
}

output "cluster_endpoint" {
  description = "The endpoint of the GKE cluster"
  value       = google_container_cluster.primary.endpoint
}

output "cluster_location" {
  description = "The location of the GKE cluster"
  value       = google_container_cluster.primary.location
}

output "database_connection_name" {
  description = "The connection name for the CloudSQL instance"
  value       = google_sql_database_instance.langflow_db.connection_name
}

output "database_private_ip" {
  description = "The private IP address of the CloudSQL instance"
  value       = google_sql_database_instance.langflow_db.private_ip_address
}

output "database_name" {
  description = "The name of the database"
  value       = google_sql_database.langflow.name
}

output "database_user" {
  description = "The database user name"
  value       = google_sql_user.langflow_user.name
}

output "redis_host" {
  description = "The host address of the Redis instance"
  value       = google_redis_instance.langflow_cache.host
}

output "redis_port" {
  description = "The port of the Redis instance"
  value       = google_redis_instance.langflow_cache.port
}

output "vpc_name" {
  description = "The name of the VPC network"
  value       = google_compute_network.vpc.name
}

output "vpc_self_link" {
  description = "The self-link of the VPC network"
  value       = google_compute_network.vpc.self_link
}

output "subnet_name" {
  description = "The name of the subnet"
  value       = google_compute_subnetwork.subnet.name
}

output "subnet_self_link" {
  description = "The self-link of the subnet"
  value       = google_compute_subnetwork.subnet.self_link
}

output "node_pool_name" {
  description = "The name of the node pool"
  value       = google_container_node_pool.primary_nodes.name
}

output "workload_identity_pool" {
  description = "The Workload Identity pool for the cluster"
  value       = "${var.project_id}.svc.id.goog"
} 