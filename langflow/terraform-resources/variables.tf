variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "arctic-moon-463710-t0"
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "db_name" {
  description = "CloudSQL database name for Langflow"
  type        = string
  default     = "langflow"
}

variable "db_user" {
  description = "CloudSQL user for Langflow"
  type        = string
  default     = "langflow"
}

variable "db_password" {
  description = "CloudSQL user password (set via TF_VAR_db_password env var or secret)"
  type        = string
  sensitive   = true
} 