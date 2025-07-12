variable "project_id" {
  description = "The ID of the project to deploy to"
  type        = string
  default     = "arctic-moon-463710-t0"
}

variable "region" {
  description = "The region to deploy to"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The zone to deploy to"
  type        = string
  default     = "us-central1-a"
}

variable "cluster_name" {
  description = "The name of the GKE cluster"
  type        = string
  default     = "x-sre-agents-cluster"
}

variable "node_count" {
  description = "The number of nodes in the node pool"
  type        = number
  default     = 3
}

variable "min_node_count" {
  description = "The minimum number of nodes in the node pool"
  type        = number
  default     = 1
}

variable "max_node_count" {
  description = "The maximum number of nodes in the node pool"
  type        = number
  default     = 10
}

variable "machine_type" {
  description = "The machine type for the nodes"
  type        = string
  default     = "e2-standard-4"
}

variable "db_password" {
  description = "The password for the database user"
  type        = string
  sensitive   = true
  default     = "langflow-password-123"
} 