terraform {
  backend "gcs" {
    bucket  = "x-sre-agents-tfstate"
    prefix  = "terraform/state"
  }
} 