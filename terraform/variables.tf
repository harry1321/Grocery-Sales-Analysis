# Define variables
variable "project_id" {
  description = "The project ID to deploy resources."
  type        = string
  default     = "datacamp-nytaxi-dbt-2025"
}

variable "region" {
  description = "The region to deploy resources."
  type        = string
  default     = "us-west1"
}

variable "zone" {
  description = "The zone to deploy resources."
  type        = string
  default     = "us-west1-a"
}

variable "credential" {
  description = "Path of credential file"
  default     = "../configs/credential/decamp_project_terraform.json"
}