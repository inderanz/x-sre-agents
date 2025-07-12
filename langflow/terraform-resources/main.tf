provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_sql_database_instance" "langflow" {
  name             = "langflow-sql"
  database_version = "POSTGRES_15"
  region           = var.region
  settings {
    tier = "db-custom-2-7680" # 2 vCPU, 7.5GB RAM
    ip_configuration {
      private_network = google_compute_network.vpc.self_link
      require_ssl     = true
    }
    backup_configuration {
      enabled = true
    }
    availability_type = "REGIONAL"
  }
  deletion_protection = true
}

resource "google_sql_database" "langflow" {
  name     = var.db_name
  instance = google_sql_database_instance.langflow.name
}

resource "google_sql_user" "langflow" {
  name     = var.db_user
  instance = google_sql_database_instance.langflow.name
  password = var.db_password
}

resource "google_compute_network" "vpc" {
  name = "langflow-vpc"
  auto_create_subnetworks = true
}

resource "google_redis_instance" "langflow" {
  name           = "langflow-redis"
  tier           = "STANDARD_HA"
  memory_size_gb = 4
  region         = var.region
  authorized_network = google_compute_network.vpc.id
}

resource "google_compute_address" "ingress_ip" {
  name   = "langflow-ingress-ip"
  region = var.region
}

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