# Output values
output "storage_account_name" {
  value = azurerm_storage_account.storage.name
}

output "storage_account_primary_connection_string" {
  value     = azurerm_storage_account.storage.primary_connection_string
  sensitive = true
}

output "storage_account_primary_access_key" {
  value     = azurerm_storage_account.storage.primary_access_key
  sensitive = true
}

output "resource_group_name" {
  value = azurerm_resource_group.storage_rg.name
}

# SFTP User outputs
output "sftp_username" {
  value = azurerm_storage_account_local_user.sftp_user.name
}

output "sftp_password" {
  value     = azurerm_storage_account_local_user.sftp_user.password
  sensitive = true
}

output "sftp_ssh_private_key" {
  value     = tls_private_key.sftp_ssh_key.private_key_pem
  sensitive = true
}

output "sftp_ssh_public_key" {
  value = tls_private_key.sftp_ssh_key.public_key_openssh
}
