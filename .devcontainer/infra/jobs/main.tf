# Configure the Azure provider
provider "azurerm" {
  features {}

  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
  client_id       = var.client_id
  use_oidc        = true
}

# Find the resource group by tag
data "azurerm_resources" "resource_group" {
  type                = "Microsoft.Resources/resourceGroups"
  resource_group_name = ""

  required_tags = {
    github_run_id = var.run_id
    created_by    = "github-actions"
    purpose       = "cshelve-testing"
  }
}

# Find storage account in the resource group
data "azurerm_storage_account" "storage" {
  resource_group_name = element(split("/", data.azurerm_resources.resource_group.resources[0].id), 4)

  tags = {
    github_run_id = var.run_id
    created_by    = "github-actions"
    purpose       = "cshelve-testing"
  }
}

locals {
  # Clean up os and python_version for container name
  clean_os = replace(lower(var.os), "[^a-z0-9]", "")
  clean_python_version = replace(var.python_version, "[^a-z0-9]", "")

  # Create a unique container name for this job
  container_name = "job-${local.clean_os}-python${local.clean_python_version}"
}

# Create a container for this specific job
resource "azurerm_storage_container" "job_container" {
  name                  = local.container_name
  storage_account_name  = data.azurerm_storage_account.storage.name
  container_access_type = "private"
}
