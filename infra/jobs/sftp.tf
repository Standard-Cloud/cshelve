locals {
  # Clean up os and python_version for container name
  clean_os = replace(replace(lower(var.os), "-", ""), "[^a-z0-9]", "")
  clean_python_version = replace(replace(var.python_version, ".", ""), "[^a-z0-9_]", "")

  # Create a unique container name for this job
  container_name = lower("${local.clean_os}${local.clean_python_version}")
}

# Generate a random string for storage account name
resource "random_string" "username" {
  length  = 8
  special = false
  upper   = false
}

# Create a container for this specific job
resource "azurerm_storage_container" "job_sftp" {
  name                  = local.container_name
  storage_account_id    = data.azurerm_storage_account.storage.id
  container_access_type = "private"
}

# Generate an SSH key for SFTP access
resource "tls_private_key" "sftp_ssh_key_rsa" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Create local user for SFTP access
resource "azurerm_storage_account_local_user" "sftp_user" {
  name                 = random_string.username.result
  storage_account_id   = data.azurerm_storage_account.storage.id
  home_directory       = azurerm_storage_container.job_sftp.name
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
    resource_name = azurerm_storage_container.job_sftp.name
  }

  ssh_authorized_key {
    description = "RSA access key"
    key         = tls_private_key.sftp_ssh_key_rsa.public_key_openssh
  }
}
