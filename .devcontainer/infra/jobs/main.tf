# Configure the Azure provider
provider "azurerm" {
  features {}

  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
  client_id       = var.client_id
  use_oidc        = true
}

# Find storage account in the resource group
data "azurerm_storage_account" "storage" {
  name                = var.storage_account_name
  resource_group_name = var.resource_group_name
}

locals {
  # Clean up os and python_version for container name
  clean_os = replace(lower(var.os), "[^a-z0-9]", "")
  clean_python_version = replace(var.python_version, "[^a-z0-9]", "")

  # Create a unique container name for this job
  container_name = lower("sftp-job-${local.clean_os}-python${local.clean_python_version}")
}

# Create a container for this specific job
resource "azurerm_storage_container" "job_sftp" {
  name                  = local.container_name
  storage_account_id    = data.azurerm_storage_account.storage.id
  container_access_type = "private"
}
