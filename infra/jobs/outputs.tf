# Output values
output "storage_account_name" {
  value = data.azurerm_storage_account.storage.name
}

output "sftp_name" {
  value = azurerm_storage_container.job_sftp.name
}

output "sftp_username" {
  value = "${data.azurerm_storage_account.storage.name}.${azurerm_storage_account_local_user.sftp_user.name}"
}

output "sftp_password" {
  value     = azurerm_storage_account_local_user.sftp_user.password
  sensitive = true
}

output "sftp_ssh_private_key_rsa" {
  value     = tls_private_key.sftp_ssh_key_rsa.private_key_pem
  sensitive = true
}

output "storage_connection_string" {
  value     = data.azurerm_storage_account.storage.primary_connection_string
  sensitive = true
}

output "storage_access_key" {
  value     = data.azurerm_storage_account.storage.primary_access_key
  sensitive = true
}

output "storage_blob_endpoint" {
  value     = data.azurerm_storage_account.storage.primary_blob_endpoint
  sensitive = true
}
