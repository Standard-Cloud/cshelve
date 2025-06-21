# Configure the Azure provider
provider "azurerm" {
  features {}

  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
  client_id       = var.client_id
  use_oidc        = true
}

# Generate a random string for storage account name
resource "random_string" "storage_account_name" {
  length  = 16
  special = false
  upper   = false
}

# Create resource group
resource "azurerm_resource_group" "storage_rg" {
  name     = "rg-${random_string.storage_account_name.result}"
  location = "West Europe"

  tags = {
    github_run_id = var.run_id
    created_by    = "github-actions"
    purpose       = "cshelve-testing"
  }
}

# Create storage account
resource "azurerm_storage_account" "storage" {
  name                     = "st${random_string.storage_account_name.result}"
  resource_group_name      = azurerm_resource_group.storage_rg.name
  location                 = azurerm_resource_group.storage_rg.location
  account_tier             = "Standard"
  sftp_enabled             = true
  is_hns_enabled           = true
  account_replication_type = "LRS"

  tags = {
    github_run_id = var.run_id
    created_by    = "github-actions"
    purpose       = "cshelve-testing"
  }
}

# Create a container in the storage account
resource "azurerm_storage_container" "container" {
  name                  = "cshelve"
  storage_account_id    = azurerm_storage_account.storage.id
  container_access_type = "private"
}
