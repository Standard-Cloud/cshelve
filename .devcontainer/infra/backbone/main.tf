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
  name     = "rg-sftp-${random_string.storage_account_name.result}"
  location = "West Europe"

  tags = {
    github_run_id = var.run_id
    created_by    = "github-actions"
    purpose       = "cshelve-sftp-testing"
  }
}

# Create storage account
resource "azurerm_storage_account" "storage" {
  name                     = "stsftp${random_string.storage_account_name.result}"
  resource_group_name      = azurerm_resource_group.storage_rg.name
  location                 = azurerm_resource_group.storage_rg.location
  account_tier             = "Standard"
  sftp_enabled             = true
  is_hns_enabled           = true
  account_replication_type = "LRS"

  tags = {
    github_run_id = var.run_id
    created_by    = "github-actions"
    purpose       = "cshelve-sftp-testing"
  }
}

# Generate an SSH key for SFTP access
resource "tls_private_key" "sftp_ssh_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Create local user for SFTP access
resource "azurerm_storage_account_local_user" "sftp_user" {
  name                 = "cshelveuser"
  storage_account_id   = azurerm_storage_account.storage.id
  home_directory       = "upload"
  ssh_password_enabled = true
  ssh_key_enabled      = true

  permission_scope {
    permissions {
      read   = true
      write  = true
      delete = true
      list   = true
      create = true
    }
    service       = "blob"
    resource_name = azurerm_storage_account.storage.name
  }

  ssh_authorized_key {
    description = "SFTP access key"
    key         = tls_private_key.sftp_ssh_key.public_key_openssh
  }
}
