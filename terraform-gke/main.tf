terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Enable required APIs
resource "google_project_service" "container" {
  service = "container.googleapis.com"
}

resource "google_project_service" "compute" {
  service = "compute.googleapis.com"
}

resource "google_project_service" "sqladmin" {
  service = "sqladmin.googleapis.com"
}

resource "google_project_service" "redis" {
  service = "redis.googleapis.com"
}

resource "google_project_service" "servicenetworking" {
  service = "servicenetworking.googleapis.com"
}

resource "google_compute_global_address" "private_ip_range" {
  name          = "x-sre-agents-private-ip-range"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
  depends_on    = [google_project_service.servicenetworking]
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_range.name]
  depends_on              = [google_project_service.servicenetworking, google_compute_global_address.private_ip_range]
}

# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "x-sre-agents-vpc"
  auto_create_subnetworks = false
}

# Subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "x-sre-agents-subnet"
  ip_cidr_range = "10.0.0.0/24"
  network       = google_compute_network.vpc.id
  region        = var.region
}

# GKE Cluster
resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = var.zone

  # Remove default node pool
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.vpc.id
  subnetwork = google_compute_subnetwork.subnet.id

  depends_on = [
    google_project_service.container,
    google_project_service.compute
  ]

  # Enable Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Enable network policy
  network_policy {
    enabled = true
  }

  # Enable horizontal pod autoscaling
  addons_config {
    horizontal_pod_autoscaling {
      disabled = false
    }
    http_load_balancing {
      disabled = false
    }
  }

  # Master authorized networks
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"
      display_name = "All"
    }
  }

  # Release channel
  release_channel {
    channel = "REGULAR"
  }
}

# Node Pool
resource "google_container_node_pool" "primary_nodes" {
  name       = "${var.cluster_name}-node-pool"
  location   = var.zone
  cluster    = google_container_cluster.primary.name
  node_count = var.node_count

  autoscaling {
    min_node_count = var.min_node_count
    max_node_count = var.max_node_count
  }

  node_config {
    machine_type = var.machine_type
    disk_size_gb = 100
    disk_type    = "pd-standard"

    # OAuth scopes
    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/compute",
      "https://www.googleapis.com/auth/devstorage.read_only"
    ]

    # Workload Identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    # Labels
    labels = {
      environment = "production"
      app         = "x-sre-agents"
    }

    # Taints
    taint {
      key    = "app"
      value  = "x-sre-agents"
      effect = "NO_SCHEDULE"
    }
  }
}

# Cloud SQL Instance (for Langflow database)
resource "google_sql_database_instance" "langflow_db" {
  name             = "langflow-db-instance"
  database_version = "POSTGRES_14"
  region           = var.region

  depends_on = [google_project_service.sqladmin, google_project_service.servicenetworking, google_service_networking_connection.private_vpc_connection]

  settings {
    tier = "db-f1-micro"
    
    backup_configuration {
      enabled    = true
      start_time = "02:00"
    }

    ip_configuration {
      ipv4_enabled    = true
      private_network = google_compute_network.vpc.id
    }
  }

  deletion_protection = false
}

# Database
resource "google_sql_database" "langflow" {
  name     = "langflow"
  instance = google_sql_database_instance.langflow_db.name
}

# Database User
resource "google_sql_user" "langflow_user" {
  name     = "langflow"
  instance = google_sql_database_instance.langflow_db.name
  password = var.db_password
}

# Redis Instance (for Langflow cache)
resource "google_redis_instance" "langflow_cache" {
  name           = "langflow-cache"
  tier           = "BASIC"
  memory_size_gb = 1
  region         = var.region

  authorized_network = google_compute_network.vpc.id

  depends_on = [google_project_service.redis]
}

# Outputs
output "cluster_name" {
  value = google_container_cluster.primary.name
}

output "cluster_endpoint" {
  value = google_container_cluster.primary.endpoint
}

output "database_connection_name" {
  value = google_sql_database_instance.langflow_db.connection_name
}

output "redis_host" {
  value = google_redis_instance.langflow_cache.host
}

output "vpc_name" {
  value = google_compute_network.vpc.name
} 