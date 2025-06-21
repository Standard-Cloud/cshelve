# Define variables for authentication
variable "subscription_id" {
  description = "Azure Subscription ID"
  type        = string
}

variable "tenant_id" {
  description = "Azure Tenant ID"
  type        = string
}

variable "client_id" {
  description = "Azure Client ID"
  type        = string
}

variable "run_id" {
  description = "GitHub Actions Run ID for tagging and finding resources"
  type        = string
}

variable "os" {
  description = "Operating system for the job container"
  type        = string
}

variable "python_version" {
  description = "Python version for the job container"
  type        = string
}

variable "storage_account_name" {
  description = "Name of the storage account created in the infrastructure job"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group containing the storage account"
  type        = string
}
